# Student Assignment Upload Portal

Flask backend with an HTML, CSS, and JavaScript frontend.

Uploads are stored in an Amazon S3 bucket.

## Environment

Create `.env` from `.env.example` and set your real bucket name:

```env
S3_BUCKET_NAME=your-s3-bucket-name
AWS_REGION=ap-south-1
S3_PREFIX=assignments
```

On EC2, attach an IAM role to the instance. `boto3` automatically uses that role through the EC2 metadata service, so no AWS access keys are needed in `.env`.

Minimum IAM permissions for the EC2 instance role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-s3-bucket-name",
        "arn:aws:s3:::your-s3-bucket-name/assignments/*"
      ]
    }
  ]
}
```

Replace `your-s3-bucket-name` with your actual bucket name.

## Run

```powershell
cd R:\Cloud\assignment_portal
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Endpoints

```text
POST /upload
GET /files
GET /download/<filename>
```
