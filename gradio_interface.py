import gradio as gr

from weaviate_service import WeaviateService


class GradioInterface:
    """Gradio interface for the movie search application."""

    def __init__(self, weaviate_service: WeaviateService):
        self.weaviate_service = weaviate_service

    def search_movies(self, query: str):
        """Search function for Gradio interface."""
        print(f"👤 User search request: '{query}'")
        results, error = self.weaviate_service.search_movies(query)

        if error:
            print(f"❌ Search failed: {error}")
            return error

        print("✅ Search results returned to user")
        return results

    def create_interface(self):
        """Create and return the Gradio interface."""

        with gr.Blocks(
            title="Movie Search Demo with Weaviate", theme=gr.themes.Soft()
        ) as demo:
            gr.Markdown("# Movie Search Demo with Weaviate")
            gr.Markdown(
                "Search through a database of movies using semantic search powered by Weaviate."
            )

            query_input = gr.Textbox(
                label="Search Query",
                placeholder="Enter your search query (e.g., 'dystopian future', 'romantic comedy', 'action movies')",
                interactive=True,
            )
            search_btn = gr.Button("Search", variant="primary")

            results_output = gr.Textbox(
                label="Search Results",
                lines=20,
                max_lines=30,
                interactive=False,
                show_copy_button=True,
            )

            # Event handlers
            search_btn.click(
                fn=self.search_movies, inputs=[query_input], outputs=[results_output]
            )

            query_input.submit(
                fn=self.search_movies, inputs=[query_input], outputs=[results_output]
            )

        return demo
