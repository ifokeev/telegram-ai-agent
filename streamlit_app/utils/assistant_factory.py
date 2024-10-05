from phi.assistant.assistant import Assistant
from phi.llm.openai.chat import OpenAIChat


def create_phi_assistant(assistant_data):
    """
    Factory method to create a phi Assistant instance from assistant_data.

    Args:
        assistant_data: An object containing assistant attributes like name, api_key, description, and instructions.

    Returns:
        Assistant: An instance of phi's Assistant class.
    """
    # Ensure instructions are in a list format
    if isinstance(assistant_data.instructions, str):
        instructions_list = assistant_data.instructions.split("\n")
    else:
        instructions_list = assistant_data.instructions

    # Create OpenAIChat instance
    openai_chat = OpenAIChat(api_key=assistant_data.api_key)

    # Create Assistant instance
    phi_assistant = Assistant(
        llm=openai_chat,
        run_id=assistant_data.name,
        description=assistant_data.description,
        instructions=instructions_list,
        add_datetime_to_instructions=True,
    )
    return phi_assistant
