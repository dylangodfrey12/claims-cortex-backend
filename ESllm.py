# ESllm.py

# This script create the email which will be sent to the insurance company 
# The prefix "ES" stands for Email Summarizer.

import anthropic
from Mfile_upload import load_system_prompt

def summarize_email(Difference, summary_text, full_arguments, isSiding: bool):
    # Initialize the Anthropic client
    api_key = "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"
    client = anthropic.Anthropic(api_key=api_key)
    
    if isSiding:
        Difference ='```\n-Maintaining Siding Matching and Uniformity\n- Partial Siding Approval Repairability\n-Detach and Reset Aluminum Siding Argument\n```'
        
    # Specify the path to the system prompt file
    system_prompt_path = "ES_systemprompt.txt"
    # Load the system prompt from the file
    system_prompt = load_system_prompt(system_prompt_path)
    
    # Define the user message
    user_message = f"""
        ## Major Rules:
    ## ALWAYS BE ASKING QUESTIONS, THAT PERTAIN TO WHAT YOU ARE ARUGING FOR.
    ### 1: DO NOT ASSUME THE USER WILL BE MAKING ANY UPDATES TO YOUR EMAIL, PLACING "[Insert detailed justifications and third-party evidence]", or anything similar to it, IS WRONG BECAUSE IT ASSUMES THE USER IS GOING TO EDIT THE EMAIL.
    ### 2: Place a heavy explicit emphasis of on the evidence. Meaning that you should explicitly incorporate evidence into your argument. Not at the bottom of the argument.
    ### 3: Never place anything pass the end of the email. If you feel the need to place evidence at the end of the email it should be used in the body of the argument.
    ### 4: *At the end of every argument in the body of the email, not the end of the email , ask a general, strategic question to the adjuster that seems like an innocent request for clarification. The question should subtly force the adjuster to either agree with your argument or provide a weak justification for denial. Your goal is to make it difficult for the adjuster to deny your claim without appearing confrontational.
            ### Ensure the questions come off as very soft and not to hard on the nose. Adjusters have huge egos and have power trips and the last thing they want is someone sounding agressive or condescending.
            -Example flow: **This is the most important part of your email**
                -Argument or statement proving something.
                -Question to the adjuster about what you just stated.
                -Argument or statement proving something.
                -Question to the adjuster about what you just stated.
                ...
                ###Never place these below the end of your email.
    ### 5: **This is an email directly to the insurance adjuster working on the insurance claim for our client.

    

        Structure of the Email:
        *Open by noting that you have read listing the items you believe should be included in totality before getting into the detailed arguments. Don't reveal the specific argument titles, but give an overview of what you will be arguing and why.*
        *Note the in-depth justifications and third-party backup attached to the main email. But do not place them in the email, only mention you have more evidence attached to the email*
        *Use transitions like "Because of this, we now must consider..." to create a logical flow and natural progression between arguments.*
        *After covering the main points, note that you have provided more in-depth justifications with third-party evidence below for them to reference if needed.*
        *Close by reiterating your key arguments and recommendations in a concise, friendly manner.*

        Tone and Style:
        *Write in a conversational, friendly, and professional tone as if speaking to a friend in person. Be kind and relaxed but never rude.*
        *Demonstrate that you have carefully reviewed the information they submitted, including details about the insurance claim and associated paperwork. Base your justifications on these documents.*
        *Get straight to the point about the arguments you will make. Present them directly in the email body rather than in a bulleted list.*

        Content to Include:
				### *The specific missing items that need to be argued for, as indicated by what is below:*
				{Difference}

				### *A rough summary of the overall flow and key points of the arguments, as provided below*
				
				{summary_text}
				
				### *The complete, fleshed out arguments that you must incorporate into the email, as provided below:*
				
				{full_arguments}
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
    