from utils.parse_pdf import extract_info_from_pdf
from graph_flow import run_vc_analysis


page_content, whole_text = extract_info_from_pdf("test_pitch_solea.pdf")

print(page_content)
print(whole_text)

run_vc_analysis(page_content, whole_text)

