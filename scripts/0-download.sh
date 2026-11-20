#!/bin/sh
# Downloads the IBM Telco customer churn sample (Apache 2.0) into work/. Pinned to one commit.
set -e
mkdir -p work
curl -sSfL -o work/Telco-Customer-Churn.csv "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/d5371f5d83a446ad5673cbcca3b814b926491f8a/data/Telco-Customer-Churn.csv"
echo "Downloaded to work/"
