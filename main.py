import threading

from gradio_interface import GradioInterface
from weaviate_service import WeaviateService


def main():
    """Main function to orchestrate the application."""
    # Initialize Weaviate service
    weaviate_service = WeaviateService()

    # Initialize Weaviate in a separate thread to avoid blocking
    init_thread = threading.Thread(target=weaviate_service.initialize)
    init_thread.daemon = True
    init_thread.start()

    # Create Gradio interface
    gradio_interface = GradioInterface(weaviate_service)
    demo = gradio_interface.create_interface()

    # Launch the application
    demo.launch(server_name="0.0.0.0", server_port=8008, share=False, show_error=True)


if __name__ == "__main__":
    main()
