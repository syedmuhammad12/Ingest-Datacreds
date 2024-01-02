from django.urls import path
from file_management import views

urlpatterns = [
    path("upload/", views.FileUpload.as_view()),
    path("convert_pdf_img/", views.ConvertPDFtoImage.as_view()),
    path("email/", views.EmailAttachmentsDownload.as_view()),
    path("sharepoint/", views.SharePointFilesDownload.as_view()),
    path("list/", views.FileListing.as_view()),
    path("view/<int:file_id>/<int:page_no>", views.ViewFile.as_view()),
    path("convert/", views.ConvertPdfToImage.as_view()),
    path("upload_extracted_data/<int:file_id>", views.UploadExtractedData.as_view())
]

