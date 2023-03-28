import boto3
from django.shortcuts import render

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        s3 = boto3.client('s3',
                          aws_access_key_id='your_access_key_id',
                          aws_secret_access_key='your_secret_access_key',
                          region_name='your_region'
                          )
        file = request.FILES['file']
        filename = file.name
        content_type = file.content_type
        multipart_upload = s3.create_multipart_upload(Bucket='your_bucket_name', Key=filename)
        upload_id = multipart_upload['UploadId']
        parts = []
        part_number = 1
        chunk_size = 1024 * 1024 * 5 # 5 MB chunk size
        file_size = file.size
        num_parts = file_size // chunk_size + (file_size % chunk_size != 0)
        try:
            while chunk_size * (part_number - 1) < file_size:
                start_byte = chunk_size * (part_number - 1)
                end_byte = min(chunk_size * part_number - 1, file_size - 1)
                response = s3.upload_part(Bucket='your_bucket_name',
                                          Key=filename,
                                          PartNumber=part_number,
                                          UploadId=upload_id,
                                          Body=file.read(chunk_size),
                                          ContentLength=end_byte - start_byte + 1,
                                          )
                parts.append({
                    'ETag': response['ETag'],
                    'PartNumber': part_number
                })
                part_number += 1
        except Exception as e:
            s3.abort_multipart_upload(Bucket='your_bucket_name', Key=filename, UploadId=upload_id)
            raise e
        else:
            s3.complete_multipart_upload(Bucket='your_bucket_name', Key=filename,
                                          MultipartUpload={
                                              'Parts': parts
                                          },
                                          UploadId=upload_id)
            return render(request, 'upload_success.html')
    return render(request, 'upload_form.html')
