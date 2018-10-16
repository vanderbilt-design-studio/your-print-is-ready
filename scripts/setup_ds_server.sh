
# Update iot.vanderbilt.design DNS record with current EC2 instance info (special thanks to https://www.lambrospetrou.com/articles/aws-update-route53-recordset-diy-load-balancer/)
IP=$( curl http://169.254.169.254/latest/meta-data/public-ipv4 )  
HOSTED_ZONE_ID=$( aws route53 list-hosted-zones-by-name | grep -B 1 -e "iot.vanderbilt.design" | sed 's/.*hostedzone\/\([A-Za-z0-9]*\)\".*/\1/' | head -n 1 )

INPUT_JSON='{
  "Comment": "Update the A record set to the new EC2 instance public IP",
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "iot.vanderbilt.design",
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


# Acquire SSL Certificate, waiting 15 seconds for propagation to complete (special thanks to https://certbot-dns-route53.readthedocs.io/en/latest/)
EMAIL=moc.liamg@sdtlibrednav
len=${#EMAIL}
for ((i=1;i<len;i++)); do EMAIL=$EMAIL${EMAIL: -i*2:1}; done; EMAIL=${EMAIL:len-1}
certbot certonly --dns-route53 --dns-route53-propagation-seconds 15 -d iot.vanderbilt.design --email $EMAIL --agree-tos -n


mkdir /opt/your-print-is-ready || rm -rf /opt/your-print-is-ready/*
