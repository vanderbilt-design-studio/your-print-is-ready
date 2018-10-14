
# Update iot.vanderbilt.design DNS record with current EC2 instance info
IP=$( curl http://169.254.169.254/latest/meta-data/public-ipv4 )  
HOSTED_ZONE_ID=$( aws route53 list-hosted-zones-by-name | grep -B 1 -e "iot.vanderbilt.design" | sed 's/.*hostedzone\/\([A-Za-z0-9]*\)\".*/\1/' | head -n 1 )

INPUT_JSON='{
  "Comment": "Update the A record set to the new EC2 instance public IP",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "test.lambrospetrou.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "127.0.0.1"
          }
        ]
      }
    }
  ]
}'

INPUT_JSON=$( echo $INPUT_JSON | sed "s/127\.0\.0\.1/$IP/" )
# http://docs.aws.amazon.com/cli/latest/reference/route53/change-resource-record-sets.html
# We want to use the string variable command so put the file contents (batch-changes file) in the following JSON
INPUT_JSON="{ \"ChangeBatch\": $INPUT_JSON }"
aws route53 change-resource-record-sets --hosted-zone-id "$HOSTED_ZONE_ID" --cli-input-json "$INPUT_JSON"



mkdir -p your-print-is-ready
rm -rf /opt/your-print-is-ready/*
