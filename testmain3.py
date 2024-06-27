# testmain3.py
# this script is used to run the functions responsible for reading estimats and making arguments.

# If the user uploads an estimate and measurements this script will run.

import threading
from Xllm import XactimateExtractor
from Mllm import MeasurementExtractor
from Ellm import EstimateGenerator as ContractorEstimateGenerator
from Cllm import EstimateComparator
from Dllm import ArgumentSelector
from AOllm import ArgumentOrganizer
from RA import RetrievalProcessor
from ASllm import ArgumentSummarizer
from ESllm import summarize_email
from voice import generate_audio
from RE import RetrievalEvidenceProcessor
from openlink import open_links

def generate_audio_thread(summary_text):
    generate_audio(summary_text)

def generate_email_summary_thread(differences, summary_text, full_arguments):
    email_summary = summarize_email(differences, summary_text, full_arguments)
    print("Email Summary:")
    print(email_summary)
    print()

if __name__ == "__main__":

    # Create an instance of the XactimateExtractor
    xactimate_extractor = XactimateExtractor()

    # Extract the insurance company's estimate using Xllm.py
    insurance_estimate = xactimate_extractor.extract_estimate()
    print("Insurance Company's Estimate:")
    print(insurance_estimate)
    print()

    # Create an instance of the MeasurementExtractor
    measurement_extractor = MeasurementExtractor()

    # Extract measurements from the contractor's PDF using Mllm.py
    contractor_measurements = measurement_extractor.extract_measurements()
    print("Extracted Measurements:")
    print(contractor_measurements)
    print()

    # Create an instance of the ContractorEstimateGenerator
    contractor_estimate_generator = ContractorEstimateGenerator()

    # Generate the contractor's estimate using Ellm.py
    contractor_estimate = contractor_estimate_generator.generate_estimate(contractor_measurements)
    print("Contractor's Estimate:")
    print(contractor_estimate)
    print()

    # Create an instance of the EstimateComparator
    comparator = EstimateComparator()

    # Compare the estimates using Cllm.py
    differences = comparator.compare_estimates(contractor_estimate, insurance_estimate)
    print("Differences between Contractor's and Insurance Company's Estimates:")
    print(differences)
    print()

    # Create an instance of the ArgumentGenerator from Dllm.py
    argument_generator = ArgumentSelector()

    # Generate arguments based on the differences using Dllm.py
    arguments = argument_generator.generate_arguments(differences)
    print("Selected Arguments to be Distributed to Master Models:")
    print(arguments)
    print()

    # Create an instance of the ArgumentOrganizer
    argument_organizer = ArgumentOrganizer()

    # Organize the arguments using AOllm.py
    organized_arguments = argument_organizer.organize_arguments(arguments)
    print("Organized Arguments:")
    print(organized_arguments)
    print()

    # Create an instance of the RetrievalProcessor
    retrieval_processor = RetrievalProcessor()

    # Process the organized arguments using R.py
    retrieval_processor.process_components(organized_arguments)
    print()

    # Print the full arguments
    print("Full Arguments:")
    print(retrieval_processor.full_arguments)

    # Create an instance of the ArgumentSummarizer
    argument_summarizer = ArgumentSummarizer()

    # Summarize the organized arguments using ASllm.py
    summary_text = argument_summarizer.summarize_arguments(organized_arguments)
    print("Summary of Arguments:")
    print(summary_text)
    print()

    # Create threads for audio generation and email summary generation
    audio_thread = threading.Thread(target=generate_audio_thread, args=(summary_text,))
    email_thread = threading.Thread(target=generate_email_summary_thread, args=(differences, summary_text, retrieval_processor.full_arguments))

    # Start both threads
    audio_thread.start()
    email_thread.start()

    # Wait for both threads to complete
    audio_thread.join()
    email_thread.join()

    # Create an instance of the RetrievalEvidenceProcessor
    retrieval_evidence_processor = RetrievalEvidenceProcessor()

    # Process the organized arguments using RE.py
    retrieval_evidence_processor.process_components(organized_arguments)
    print()

    # Print the full evidence
    print("Full Evidence:")
    print(retrieval_evidence_processor.full_evidence)

    # Open the links in the full evidence
    open_links(retrieval_evidence_processor.full_evidence)

