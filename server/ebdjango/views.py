from rest_framework.decorators import api_view
from wsgiref.util import FileWrapper
from django.http import HttpResponse, JsonResponse
from .source.RunDiagramAnim import render_animation
import logging

@api_view(['POST'])
def test(request):
    # try:
    #     logging.basicConfig(filename="/opt/python/python_log.log",
    #                         format='%(asctime)s %(message)s',
    #                         filemode='w')
    #     logger = logging.getLogger()
    #     logger.setLevel(logging.DEBUG)
    # except Exception as error:
    #     return JsonResponse({"status": "OK", "error": str(error)}, status=200)
    
    if request.method == 'POST':
        # try:
        #     logger.debug("Debug message")
        # except Exception as error:
        #     return JsonResponse({"status": "OK", "error": str(error)}, status=200)
        
        styles = request.data['stylesInput']
        tikz_inputs = [diagram['tikz'] for diagram in request.data['diagrams'].values()]
        extra_info = {int(id): {key: value for key, value in diagram.items() if key != 'tikz'} for id, diagram in request.data['diagrams'].items()}
        try:
            render_animation('tikzit', styles, tikz_inputs, extra_info)
        except Exception as error:
            print("Error:", error)
            return JsonResponse({"error": str(error)}, status=500)
            
        file = FileWrapper(open('./media/videos/480p15/DiagramScene.mp4', 'rb'))
        response = HttpResponse(file, content_type='video/mp4')
        response['Content-Disposition'] = 'attachment; filename=animation.mp4'
        print("Ready to return response")
        return response
    

@api_view(['GET'])
def health_check(request):
    return JsonResponse({"status": "OK"}, status=200)
        
