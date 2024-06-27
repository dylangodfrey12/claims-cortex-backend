def get_adjuster_email():
    adjuster_email = (f"""Dear [Insured's Name],
Thank you for submitting your property insurance claim. After careful review of the claim and
assessment of the repair requirements detailed, we regret to inform you that your claim cannot
be approved based on the terms of your insurance policy.
Our evaluation determined that the inclusion of a starter strip is considered part of the waste
factor for materials required in standard roofing repairs and replacements. As such, it is
accounted for within the original estimation of materials needed and does not warrant additional
coverage.
Additionally, the claim does not meet the criteria required for the allocation of overhead and
profit. The nature of the job, involving only the roofing trade, does not exhibit the complexity
typically necessitating multiple trades or extensive coordination that would justify additional
overhead and profit costs.

""")
    return adjuster_email

def load_system_prompt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        system_prompt = file.read()
    return system_prompt

