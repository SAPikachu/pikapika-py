def is_form_request(request):
    content_type = request.META["CONTENT_TYPE"].lower()
    return (
        content_type.startswith("application/x-www-form-urlencoded") or 
        content_type.startswith("multipart/")
    )
