from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .services.download_service import find_file_by_substring
from .services.helper_service import prepare_filters, filter_base_dataframe
from .services.extractor_service import extract
import threading
# Create your views here.
# myapp/views.py



# myapp/views.py
global progress
global goal
global uf
global zn
global sc

def basic_view(request):
    return render(request, 'index.html')


def extractor_view(request):
    PAGE = 'index.html'
    
    DATA_PATH = "."
    all_candidates_file_sub_str = "candidato"
    all_sections_file_sub_str = "secao"
    
    candidates_file_path = find_file_by_substring(DATA_PATH, all_candidates_file_sub_str)
    sections_file_path = find_file_by_substring(DATA_PATH, all_sections_file_sub_str)
    
    filters = prepare_filters(sections_file_path)
    filters["TURNO"] = [1,2]
    
    # Handle form submission with selected filters
    if request.method == "POST":
        global progress
        global goal
        global uf
        
        progress = 0
        uf = "Not Started"
        
        selected_filters = {}
        print(request.POST)
        for filter_name in filters.keys():
            selected_filters[filter_name] = [request.POST.get(filter_name)]

        turno = selected_filters.pop("TURNO", 1)[0]
        # Filter the DataFrame using the selected filters
        filtered_data = filter_base_dataframe(selected_filters, sections_file_path)
        goal = filtered_data.shape[0]
        
        # Call the extract function to fetch candidate data
        # Start the extraction in a background thread
        extraction_thread = threading.Thread(target=extract, args=(filtered_data, candidates_file_path, progress_callback, turno))
        extraction_thread.start()  # This starts the background thread

        data = {
            "candidates_file_path": candidates_file_path,
            "sections_file_path": sections_file_path,
            "filters": filters
        }

    else:
        # On GET request, just render the page with available filters
        data = {
            "candidates_file_path": candidates_file_path,
            "sections_file_path": sections_file_path,
            "filters": filters,
        }

    return render(request, PAGE, data)


def progress_callback(new_progress, new_goal, new_uf):
    global progress
    global goal
    global uf
    
    progress = new_progress
    goal = new_goal
    uf = new_uf
    return JsonResponse({"progress": progress, "goal":goal, "uf":uf})
    


def get_progress(request):
    global progress
    global goal
    global uf
    percentage = int(progress / goal * 100)
    return JsonResponse({"progress": progress, "percentage":percentage, "goal":goal, "uf":uf})


def get_base_information(request):
    pass