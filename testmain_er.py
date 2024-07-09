# testmain3.py
# this script is used to run the functions responsible for reading estimats and making arguments.

# If the user uploads an estimate and measurements this script will run.

import threading
import asyncio
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
from er_llm import ErIcGenerator
from sor_llm import SorEvaluator
from sm_llm import SmEvaluator
from se_llm import SeEvaluator
from main import generateFrpmEmail

# pdf_path_estimate = r"C:\Users\dylan\Downloads\BackendMVP\test_data_6_estimate.pdf"
# pdf_path_measurements = r"C:\Users\dylan\Downloads\BackendMVP\test_data_6_measurements.pdf"


def generate_audio_thread(summary_text):
    generate_audio(summary_text)

def generate_email_summary_thread(differences, summary_text, full_arguments):
    email_summary = summarize_email(differences, summary_text, full_arguments)
    print("Email Summary:")
    print(email_summary)
    print()

# Define the print_to_text_file method
def print_to_text_file(text_to_print):
    with open('output.txt', 'a') as f:
        print(text_to_print, file=f)

# Define the generate_full_er_estimate method
# async def generate_full_er_estimate():
#     # Create an instance of the XactimateExtractor
#     xactimate_extractor = XactimateExtractor()

#     # Extract the insurance company's estimate using Xllm.py
#     insurance_estimate = xactimate_extractor.extract_estimate(pdf_path_estimate)
#     print_to_text_file("Insurance Company's Estimate:")
#     print_to_text_file(insurance_estimate)
#     print_to_text_file("")

#     # Create an instance of the MeasurementExtractor
#     measurement_extractor = MeasurementExtractor()

#     # Extract measurements from the contractor's PDF using Mllm.py
#     contractor_measurements = measurement_extractor.extract_measurements(pdf_path_measurements)
#     print_to_text_file("Extracted Measurements:")
#     print_to_text_file(contractor_measurements)
#     print_to_text_file("")

#     # Create an instance of the ContractorEstimateGenerator
#     contractor_estimate_generator = ContractorEstimateGenerator()

#     # Generate the contractor's estimate using Ellm.py
#     contractor_estimate = contractor_estimate_generator.generate_estimate(contractor_measurements)
    
#     ic_director = IcEvaluator()
    
#     ic_director_type = await ic_director.IcDeterminer(contractor_measurements, contractor_estimate, insurance_estimate)
#     print_to_text_file("start ic director type")
#     print_to_text_file(ic_director_type)
#     print_to_text_file("end ic director type")
#     # Create an instance of the EstimateComparator
#     comparator = EstimateComparator()

#     # Compare the estimates using Cllm.py
#     differences = comparator.compare_estimates(contractor_estimate, insurance_estimate)
#     print_to_text_file("start differences")
#     print_to_text_file("Differences between Contractor's and Insurance Company's Estimates:")
#     print_to_text_file(differences)
#     print_to_text_file("differences")

#     # Create an instance of the ArgumentGenerator from Dllm.py
#     argument_generator = ArgumentSelector()

#     # Generate arguments based on the differences using Dllm.py
#     arguments = argument_generator.generate_arguments(differences)
#     print_to_text_file("Selected Arguments to be Distributed to Master Models:")
#     print_to_text_file(arguments)

#     # Create an instance of the ArgumentOrganizer
#     argument_organizer = ArgumentOrganizer()

#     # Organize the arguments using AOllm.py
#     organized_arguments = argument_organizer.organize_arguments(arguments)
#     print_to_text_file("Organized Arguments:")
#     print_to_text_file(organized_arguments)

#     # Create an instance of the RetrievalProcessor
#     retrieval_processor = RetrievalProcessor()

#     # Process the organized arguments using R.py
#     retrieval_processor.process_components(organized_arguments)

#     # Print the full arguments
#     print_to_text_file("Full Arguments:")
#     print_to_text_file(retrieval_processor.full_arguments)

#     # Create an instance of the ArgumentSummarizer
#     argument_summarizer = ArgumentSummarizer()

#     # Summarize the organized arguments using ASllm.py
#     summary_text = argument_summarizer.summarize_arguments(organized_arguments)
#     print_to_text_file("Summary of Arguments:")
#     print_to_text_file(summary_text)

#     # Create threads for audio generation and email summary generation
#     audio_thread = threading.Thread(target=generate_audio_thread, args=(summary_text,))
#     email_thread = threading.Thread(target=generate_email_summary_thread, args=(differences, summary_text, retrieval_processor.full_arguments))

#     # Start both threads
#     audio_thread.start()
#     email_thread.start()

#     # Wait for both threads to complete
#     audio_thread.join()
#     email_thread.join()

#     # Create an instance of the RetrievalEvidenceProcessor
#     retrieval_evidence_processor = RetrievalEvidenceProcessor()

#     # Process the organized arguments using RE.py
#     retrieval_evidence_processor.process_components(organized_arguments)

#     # Print the full evidence
#     print_to_text_file("Full Evidence:")
#     print_to_text_file(retrieval_evidence_processor.full_evidence)

#     # Open the links in the full evidence
#     open_links(retrieval_evidence_processor.full_evidence)

# single elevation or full
async def generate_fs_estimate():
    pdf_path_estimate = r"C:\Users\dylan\Downloads\BackendMVP\td2_estimate_fs.pdf"
    pdf_path_measurements = r"C:\Users\dylan\Downloads\BackendMVP\td2_measurements_fs.pdf"
    insurance_estimate= process_estimates_and_measurements(pdf_path_estimate)

    # ic dIRECTOR START
    sor_director = SorEvaluator()
    # returns IC type
    sor_director_repair_type = await sor_director.run_and_compare_ic_determiner(insurance_estimate)
    

    result = await sor_director.route_arguments_from_determiner(sor_director_repair_type,  insurance_estimate, pdf_path_measurements)
       # Access the return values
    summary_text,  full_evidence , audio_url, full_arguments, differences, organized_arguments = result
    
    # Do something with the results
    print("Full Arguments:", full_arguments)
    print("Full Evidence:", full_evidence)

    # Summarize the organized arguments using ASllm.py
    print_to_text_file("Summary of Arguments:")
    print_to_text_file(summary_text)
    print_to_text_file("Full Evidence:")
    print_to_text_file(full_evidence)

    # Open the links in the full evidence
    # open_links(full_evidence)
    return result


async def generate_fr_estimate():
    pdf_path_estimate = r"C:\Users\dylan\Downloads\BackendMVP\test_data_6_estimate.pdf"
    pdf_path_measurements = r"C:\Users\dylan\Downloads\BackendMVP\test_data_6_measurements.pdf"
    
    insurance_estimate= process_estimates_and_measurements(pdf_path_estimate)

    # ic dIRECTOR START
    sor_director = SorEvaluator()
    # returns IC type
    sor_director_repair_type = await sor_director.run_and_compare_ic_determiner(insurance_estimate)
    

    result = await sor_director.route_arguments_from_determiner(sor_director_repair_type,  insurance_estimate, pdf_path_measurements)
       # Access the return values
    summary_text,  full_evidence , audio_url, full_arguments, differences, organized_arguments = result
    
    # Do something with the results
    print("Full Arguments:", full_arguments)
    print("Full Evidence:", full_evidence)

    # Summarize the organized arguments using ASllm.py
    print_to_text_file("Summary of Arguments:")
    print_to_text_file(summary_text)
    print_to_text_file("Full Evidence:")
    print_to_text_file(full_evidence)

    # Open the links in the full evidence
    # open_links(full_evidence)
    return result


async def generate_se_report():
    pdf_path_estimate = r"C:\Users\dylan\Downloads\BackendMVP\td1_estimate_se.pdf"
    pdf_path_measurements = r"C:\Users\dylan\Downloads\BackendMVP\td1_measurements_se.pdf"
    
    insurance_estimate= process_estimates_and_measurements(pdf_path_estimate)

    # ic dIRECTOR START
    sor_director = SorEvaluator()
    # returns IC type
    sor_director_repair_type = await sor_director.run_and_compare_ic_determiner(insurance_estimate)
    

    result = await sor_director.route_arguments_from_determiner(sor_director_repair_type,  insurance_estimate, pdf_path_measurements)
       # Access the return values
    summary_text,  full_evidence , audio_url, full_arguments, differences, organized_arguments = result
    
    # Do something with the results
    print("Full Arguments:", full_arguments)
    print("Full Evidence:", full_evidence)

    # Summarize the organized arguments using ASllm.py
    print_to_text_file("Summary of Arguments:")
    print_to_text_file(summary_text)
    print_to_text_file("Full Evidence:")
    print_to_text_file(full_evidence)

    # Open the links in the full evidence
    # open_links(full_evidence)
    return result

async def generate_is_report():
    pdf_path_estimate = r"C:\Users\dylan\Downloads\BackendMVP\td1_estimate_is.pdf"
    pdf_path_measurements = r"C:\Users\dylan\Downloads\BackendMVP\td1_measurements_is.pdf"
    insurance_estimate= process_estimates_and_measurements(pdf_path_estimate)

    # ic dIRECTOR START
    sor_director = SorEvaluator()
    # returns IC type
    sor_director_repair_type = await sor_director.run_and_compare_ic_determiner(insurance_estimate)
    

    result = await sor_director.route_arguments_from_determiner(sor_director_repair_type,  insurance_estimate, pdf_path_measurements)
       # Access the return values
    summary_text,  full_evidence , audio_url, full_arguments, differences, organized_arguments = result
    
    # Do something with the results
    print("Full Arguments:", full_arguments)
    print("Full Evidence:", full_evidence)

    # Summarize the organized arguments using ASllm.py
    print_to_text_file("Summary of Arguments:")
    print_to_text_file(summary_text)
    print_to_text_file("Full Evidence:")
    print_to_text_file(full_evidence)

    # Open the links in the full evidence
    # open_links(full_evidence)
    return result    
    
async def generate_ss_report():
    pdf_path_estimate = r"C:\Users\dylan\Downloads\BackendMVP\td1_estimate_ss.pdf"
    pdf_path_measurements = r"C:\Users\dylan\Downloads\BackendMVP\td1_measurements_ss.pdf"
    insurance_estimate= process_estimates_and_measurements(pdf_path_estimate)

    # ic dIRECTOR START
    sor_director = SorEvaluator()
    # returns IC type
    sor_director_repair_type = await sor_director.run_and_compare_ic_determiner(insurance_estimate)
    

    result = await sor_director.route_arguments_from_determiner(sor_director_repair_type,  insurance_estimate, pdf_path_measurements)
       # Access the return values
    summary_text,  full_evidence , audio_url, full_arguments, differences, organized_arguments = result
    
    # Do something with the results
    print("Full Arguments:", full_arguments)
    print("Full Evidence:", full_evidence)

    # Summarize the organized arguments using ASllm.py
    print_to_text_file("Summary of Arguments:")
    print_to_text_file(summary_text)
    print_to_text_file("Full Evidence:")
    print_to_text_file(full_evidence)

    # Open the links in the full evidence
    # open_links(full_evidence)
    return result

async def generate_ss_report_from_main():
    pdf_path_estimate = r"C:\Users\dylan\Downloads\BackendMVP\td1_estimate_ss.pdf"
    pdf_path_measurements = r"C:\Users\dylan\Downloads\BackendMVP\td1_measurements_ss.pdf"
    insurance_estimate= process_estimates_and_measurements(pdf_path_estimate)

    # ic dIRECTOR START
    sor_director = SorEvaluator()
    # returns IC type
    sor_director_repair_type = await sor_director.run_and_compare_ic_determiner(insurance_estimate)
    

    result = await sor_director.route_arguments_from_determiner(sor_director_repair_type,  insurance_estimate, pdf_path_measurements)
       # Access the return values
    summary_text,  full_evidence , audio_url, full_arguments, differences, organized_arguments = result
    
    # Do something with the results
    print("Full Arguments:", full_arguments)
    print("Full Evidence:", full_evidence)

    # Summarize the organized arguments using ASllm.py
    print_to_text_file("Summary of Arguments:")
    print_to_text_file(summary_text)
    print_to_text_file("Full Evidence:")
    print_to_text_file(full_evidence)

    # Open the links in the full evidence
    # open_links(full_evidence)
    return result
    
async def generate_email_report():
    
    # Sample adjuster email for testing
    adjuster_email = "sample_adjuster@example.com"

    # Call the asynchronous method
    response = await generateFrpmEmail(adjuster_email=adjuster_email)

    
    return response

def process_estimates_and_measurements(pdf_path_estimate):
    # Create an instance of the XactimateExtractor
    xactimate_extractor = XactimateExtractor()

    # Extract the insurance company's estimate using Xllm.py
    insurance_estimate = xactimate_extractor.extract_estimate(pdf_path_estimate)
    print_to_text_file("Insurance Company's Estimate:")
    print_to_text_file(insurance_estimate)
    print_to_text_file("")

    return insurance_estimate

# def process_estimates_and_measurements(pdf_path_estimate, pdf_path_measurements):
#     # Create an instance of the XactimateExtractor
#     xactimate_extractor = XactimateExtractor()

#     # Extract the insurance company's estimate using Xllm.py
#     insurance_estimate = xactimate_extractor.extract_estimate(pdf_path_estimate)
#     print_to_text_file("Insurance Company's Estimate:")
#     print_to_text_file(insurance_estimate)
#     print_to_text_file("")

#     # Create an instance of the MeasurementExtractor
#     measurement_extractor = MeasurementExtractor()

#     # Extract measurements from the contractor's PDF using Mllm.py
#     contractor_measurements = measurement_extractor.extract_measurements(pdf_path_measurements)
#     print_to_text_file("Extracted Measurements:")
#     print_to_text_file(contractor_measurements)
#     print_to_text_file("")

#     # Create an instance of the ContractorEstimateGenerator
#     contractor_estimate_generator = ContractorEstimateGenerator()

#     # Generate the contractor's estimate using Ellm.py
#     contractor_estimate = contractor_estimate_generator.generate_estimate(contractor_measurements)
    
#     return insurance_estimate, contractor_measurements, contractor_estimate


if __name__ == "__main__":
    asyncio.run(generate_fr_estimate())