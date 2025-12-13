# S3 Object Compressor
## Functions

---

So far, I only cover two file formats:

- Image: PNG and JP*G
- Pdf

### Purpose

Whenever a file is uploaded to AWS S3 an event is triggered starting up an AWS Lambda function that listens
to those events.

The function will compress the file (basically compress images) and upload it to the same bucket with a different name.

### Libraries

- Boto3
- PIL
- Pikepdf
