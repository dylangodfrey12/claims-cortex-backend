import threading
from EASllm import EmailArgumentSelector
from EJllm import EmailJest
from RA import RetrievalProcessor
from ASEllm import ArgumentSummarizerEmail
from EFEllm import EmaiFromEmail
from voice import generate_audio
from RE import RetrievalEvidenceProcessor
from openlink import open_links

def generate_audio_thread(summary):
    generate_audio(summary)

def generate_email_thread(summary, adjuster_email, email_jest, full_arguments):
    Full_Email_Argument = EmaiFromEmail()
    final_email = Full_Email_Argument.the_email_arguments(summary, adjuster_email, email_jest, full_arguments)
    print("Email To Adjuster:")
    print(final_email)

if __name__ == "__main__":
    # Create an instance of the EmailArgumentSelector
    email_argument_selector = EmailArgumentSelector()

    # Extract arguments from the adjuster's email using EASllm.py
    email_arguments = email_argument_selector.extract_arguments()

    # Print the extracted arguments
    print("Arguments Extracted from Adjuster's Email:")
    print(email_arguments)
    print()

    # Create an instance of the EmailJest
    email_jest = EmailJest()

    # Extract what the adjuster is saying and why using EJllm.py
    adjuster_jest = email_jest.extract_arguments()

    # Print what the adjuster is saying and why
    print("What the Adjuster is Saying and Why:")
    print(adjuster_jest)

    # Create an instance of the RetrievalProcessor
    retrieval_processor = RetrievalProcessor()

    # Process the organized arguments using R.py
    retrieval_processor.process_components(email_arguments)
    print()

    # Create an instance of the ArgumentSummarizerEmail
    argument_summarizer_email = ArgumentSummarizerEmail()

    # Extract arguments from the adjuster's email using the extract_arguments method
    adjuster_email = argument_summarizer_email.extract_arguments()

    # Summarize the arguments using the summarize_arguments method
    summary = argument_summarizer_email.summarize_arguments(adjuster_email, email_jest, retrieval_processor.full_arguments)
    print("Argument Summary:")
    print(summary)

    # Create threads for audio generation and email generation
    audio_thread = threading.Thread(target=generate_audio_thread, args=(summary,))
    email_thread = threading.Thread(target=generate_email_thread, args=(summary, adjuster_email, email_jest, retrieval_processor.full_arguments))

    # Start both threads
    audio_thread.start()
    email_thread.start()

    # Wait for both threads to complete
    audio_thread.join()
    email_thread.join()

    # Create an instance of the RetrievalEvidenceProcessor
    retrieval_evidence_processor = RetrievalEvidenceProcessor()

    # Process the organized arguments using RE.py
    retrieval_evidence_processor.process_components(email_arguments)
    print()

    # Print the full evidence
    print("Full Evidence:")
    print(retrieval_evidence_processor.full_evidence)

    # Open the links in the full evidence
    open_links(retrieval_evidence_processor.full_evidence)
