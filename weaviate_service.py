import json
import os
from datetime import datetime, timezone

import pandas as pd
import requests
import weaviate
import weaviate.classes.config as wc
import weaviate.classes.query as wq
from dotenv import load_dotenv
from tqdm import tqdm
from weaviate.util import generate_uuid5


class WeaviateService:
    """Service class for handling all Weaviate operations."""

    def __init__(self):
        self.client = None
        self.is_ready = False
        self.initialization_status = "Initializing..."

    def initialize(self):
        """Initialize Weaviate client and set up collection if needed."""
        print("🚀 Starting Weaviate initialization...")
        try:
            print("📋 Loading environment variables...")
            load_dotenv()

            headers = {
                "X-OpenAI-Api-Key": os.getenv("OPENAI_APIKEY"),
            }

            print(
                f"🔌 Connecting to Weaviate at {os.getenv('WEAVIATE_HOST')}:{os.getenv('WEAVIATE_PORT')}..."
            )
            self.client = weaviate.connect_to_local(
                host=os.getenv("WEAVIATE_HOST"),
                port=os.getenv("WEAVIATE_PORT"),
                headers=headers,
            )
            print("✅ Successfully connected to Weaviate!")

            # Check if collection exists
            print("🔍 Checking for existing collections...")
            collections = self.client.collections.list_all()
            print(
                f"📊 Found {len(collections)} existing collections: {list(collections.keys())}"
            )

            if "Movie" not in collections:
                print("🎬 Movie collection not found. Creating collection...")
                self.initialization_status = "Creating collection..."
                self.create_collection()

                print("📥 Starting data import...")
                self.initialization_status = (
                    "Importing data... This may take a few minutes."
                )
                self.import_data()
            else:
                print(
                    "✅ Movie collection already exists. Skipping creation and import."
                )

            self.is_ready = True
            self.initialization_status = "Ready! You can now search for movies."
            print("🎉 Weaviate initialization completed successfully!")

        except Exception as e:
            self.initialization_status = f"Error: {str(e)}"
            self.is_ready = False
            print(f"❌ Weaviate initialization failed: {str(e)}")

    def create_collection(self):
        """Create the Movie collection in Weaviate."""
        print("🏗️  Creating Movie collection with schema...")
        print(
            "   - Properties: title, overview, vote_average, genre_ids, release_date, tmdb_id"
        )
        print("   - Vectorizer: text2vec-openai")
        print("   - Generative: openai")

        self.client.collections.create(
            name="Movie",
            properties=[
                wc.Property(name="title", data_type=wc.DataType.TEXT),
                wc.Property(name="overview", data_type=wc.DataType.TEXT),
                wc.Property(name="vote_average", data_type=wc.DataType.NUMBER),
                wc.Property(name="genre_ids", data_type=wc.DataType.INT_ARRAY),
                wc.Property(name="release_date", data_type=wc.DataType.DATE),
                wc.Property(name="tmdb_id", data_type=wc.DataType.INT),
            ],
            # Define the vectorizer module
            vector_config=wc.Configure.Vectors.text2vec_openai(),
            # Define the generative module
            generative_config=wc.Configure.Generative.openai(),
        )
        print("✅ Movie collection created successfully!")

    def import_data(self):
        """Import movie data from external source."""
        data_url = "https://raw.githubusercontent.com/weaviate-tutorials/edu-datasets/main/movies_data_1990_2024.json"
        print(f"🌐 Fetching movie data from: {data_url}")

        resp = requests.get(data_url)
        print(f"📥 Downloaded data (status: {resp.status_code})")

        df = pd.DataFrame(resp.json())
        print(f"📊 Loaded {len(df)} movies into DataFrame")

        # Get the collection
        movies = self.client.collections.use("Movie")
        print("🎬 Using Movie collection for import...")

        # Enter context manager
        print("📦 Starting batch import (batch size: 200)...")
        with movies.batch.fixed_size(batch_size=200) as batch:
            # Loop through the data
            for i, movie in tqdm(df.iterrows(), total=len(df), desc="Importing movies"):
                # Convert data types
                # Convert a JSON date to `datetime` and add time zone information
                release_date = datetime.strptime(
                    movie["release_date"], "%Y-%m-%d"
                ).replace(tzinfo=timezone.utc)
                # Convert a JSON array to a list of integers
                genre_ids = json.loads(movie["genre_ids"])

                # Build the object payload
                movie_obj = {
                    "title": movie["title"],
                    "overview": movie["overview"],
                    "vote_average": movie["vote_average"],
                    "genre_ids": genre_ids,
                    "release_date": release_date,
                    "tmdb_id": movie["id"],
                }

                # Add object to batch queue
                batch.add_object(
                    properties=movie_obj,
                    uuid=generate_uuid5(movie["id"]),
                    # references=reference_obj  # You can add references here
                )
                # Batcher automatically sends batches

        # Check for failed objects
        if len(movies.batch.failed_objects) > 0:
            print(f"❌ Failed to import {len(movies.batch.failed_objects)} objects")
        else:
            print("✅ All movies imported successfully!")

    def search_movies(self, query: str, limit: int = 10):
        """Search for movies based on query string and return formatted results."""
        print(f"🔍 Search request: '{query}' (limit: {limit})")

        if not self.is_ready or not self.client:
            print("⚠️  Search blocked - system not ready")
            return (
                None,
                f"⚠️ System is not ready yet. Please wait for initialization to complete.\n\nCurrent status: {self.initialization_status}",
            )

        if not query.strip():
            print("⚠️  Empty query provided")
            return None, "Please enter a search query."

        try:
            # Get the collection
            print("🎬 Accessing Movie collection...")
            movies = self.client.collections.use("Movie")

            # Perform query
            print(f"🔎 Executing semantic search for: '{query}'")
            response = movies.query.near_text(
                query=query,
                limit=limit,
                return_metadata=wq.MetadataQuery(distance=True),
            )

            # Format results for display
            results = []
            for o in response.objects:
                result = {
                    "title": o.properties["title"],
                    "overview": o.properties["overview"],
                    "release_date": o.properties["release_date"].year,
                    "vote_average": o.properties["vote_average"],
                    "distance": f"{o.metadata.distance:.3f}",
                }
                results.append(result)

            print(f"📊 Found {len(results)} results")

            if not results:
                print("❌ No movies found matching query")
                return None, "No movies found matching your query."

            # Format results for display
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"**{i}. {result['title']}** ({result['release_date']})\n"
                    f"Rating: {result['vote_average']}/10\n"
                    f"Overview: {result['overview'][:200]}{'...' if len(result['overview']) > 200 else ''}\n"
                    f"Similarity Score: {result['distance']}\n"
                    f"{'─' * 50}\n"
                )

            print("✅ Search completed successfully")
            return "\n".join(formatted_results), None

        except Exception as e:
            print(f"❌ Search error: {str(e)}")
            return None, f"Error searching movies: {str(e)}"

    def close(self):
        """Close the Weaviate client connection."""
        if self.client:
            print("🔌 Closing Weaviate connection...")
            self.client.close()
            print("✅ Weaviate connection closed")
