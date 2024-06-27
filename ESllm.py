# ESllm.py

# This script create the email which will be sent to the insurance company 
# The prefix "ES" stands for Email Summarizer.

import anthropic
from Mfile_upload import load_system_prompt

def summarize_email(Difference, summary_text, full_arguments):
    # Initialize the Anthropic client
    api_key = "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"
    client = anthropic.Anthropic(api_key=api_key)
    
    # Specify the path to the system prompt file
    system_prompt_path = "ES_systemprompt.txt"
    # Load the system prompt from the file
    system_prompt = load_system_prompt(system_prompt_path)
    
    # Define the user message
    user_message = f"""Structure of the Email:
*Open by noting that you have read listing the items you believe should be included in totality before getting into the detailed arguments. Don't reveal the specific argument titles, but give an overview of what you will be arguing and why.*
*For each item/argument, explain the relevant code requirements and manufacturing requirements. Refer to reputable sources and evidence to support your points.*
*Use transitions like "Because of this, we now must consider..." to create a logical flow and natural progression between arguments.*
*After covering the main points, note that you have provided more in-depth justifications with third-party evidence below for them to reference if needed.*
*Close by reiterating your key arguments and recommendations in a concise, friendly manner.*

Tone and Style:
*Write in a conversational, friendly, and professional tone as if speaking to a friend in person. Be kind and relaxed but never rude.*
*Demonstrate that you have carefully reviewed the information they submitted, including details about the insurance claim and associated paperwork. Base your justifications on these documents.*
*Get straight to the point about the arguments you will make. Present them directly in the email body rather than in a bulleted list.*

Content to Include:
*The specific missing items that need to be argued for, as indicated by what is below ensure these are idendical in the output as they are in the input:*
{Difference}

*A rough summary of the overall flow and key points of the arguments, as provided below*
{summary_text}

*The complete, fleshed out arguments that you must incorporate into the email, as provided below:*
{full_arguments}

Key Reminders:
*Refer to all relevant evidence, code requirements, manufacturer recommendations, and definitions in each section of your justifications.*
*Don't explicitly name the argument titles - instead describe the points you're making.*
*Note the in-depth justifications and third-party backup provided below the main email.*
*Ensure arguments flow logically and build upon each other.*
*Maintain a friendly, conversational tone while being direct and professional.*

"""
    
    # Send a message to the Claude 3 Opus model
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0.2,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    # Extract the plain text summary from the response
    email_summary = response.content[0].text.strip()
    
    # Return the plain text summary
    return email_summary
    