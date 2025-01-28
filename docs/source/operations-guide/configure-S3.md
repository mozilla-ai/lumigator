# Configuring S3 Storage for Lumigator

This guide will walk you through the process of configuring your S3-compatible storage for Lumigator.

## Configuration

To use Lumigator with S3 or S3-compatible storage, you need to configure CORS (Cross-Origin Resource Sharing) for your bucket. Below is the recommended CORS configuration:

```console
<?xml version="1.0" encoding="UTF-8"?>
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>*</AllowedOrigin> <!-- Replace * with your specific origin if needed -->
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <AllowedMethod>HEAD</AllowedMethod>
    <AllowedHeader>*</AllowedHeader>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
  </CORSRule>
</CORSConfiguration>
```

You can specify your origin instead of * in <AllowedOrigin> to restrict access, but a wildcard (*) will also work. Configuring this is necessary for Lumigator to function correctly with your S3 bucket.

## Applying CORS configuration

In order to apply that CORS configuration to the bucket, if you want to do it with the AWS CLI tool (our suggested method), you have to
write the CORS configuration in JSON, and store it in a file:

```console
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "POST", "PUT", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

After that, you can apply it with the AWS CLI tool:

```console
user@host:~$ aws s3api put-bucket-cors --bucket <bucket-name> --cors-configuration file://cors-config.json
```