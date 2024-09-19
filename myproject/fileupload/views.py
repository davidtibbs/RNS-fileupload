import os
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from cryptography.fernet import Fernet
from django.conf import settings
from django.utils.decorators import method_decorator


@method_decorator(
    csrf_exempt, name="dispatch"
)
class FileUploadView(View):

    def post(self, request):
        # Check for the file upload
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file provided."}, status=400)

        uploaded_file = request.FILES["file"]

        # Create a new key for encryption
        key = Fernet.generate_key()
        cipher = Fernet(key)

        # Encrypt the file
        file_content = uploaded_file.read()
        encrypted_content = cipher.encrypt(file_content)

        # Store the encrypted file in the local filesystem
        fs = FileSystemStorage()
        # Create a ContentFile from the encrypted content
        encrypted_file = ContentFile(encrypted_content)

        # Save the encrypted file
        file_name = fs.save(f"encrypted_{uploaded_file.name}", encrypted_file)

        # Save the key to the local filesystem
        key_file_name = f"key_{uploaded_file.name}.key"
        with open(os.path.join(settings.MEDIA_ROOT, key_file_name), "wb") as key_file:
            key_file.write(key)

        return JsonResponse(
            {
                "message": "File uploaded and encrypted successfully to the local file system.",
                "file_name": file_name,
                "key_file_name": key_file_name,
            }
        )
