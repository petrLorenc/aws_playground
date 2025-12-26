# Notes from Pluralsight AWS Certified Solutions Architect - Associate Course

## AWS Indentity and Management
AIM - AWS Indentity and Management
- root account - full access, avoid using it + turn MFA on it, do not create Access keys for it
- IAM users - individual users with specific permissions - human or dedicated account, implicit deny > explicit allow > explicit deny (default deny all)
- IAM groups - collection of users with same permissions, user can be in multiple groups
- IAM Policies - JSON documents that define permissions, can be attached to users, groups, or roles
   * Indentity-based policies - attached to users, groups, or roles, implicit deny, explicit allow
        * managed policies - AWS managed or customer managed (reusable)
        * inline policies - embedded in a single user, group, or role (not reusable), attached to specific identity (not visible in policies list), removed when identity is deleted
   * Resource-based policies - attached to resources like S3 buckets - always inline
   * example of IAM policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "ListExampleBucket", // optional identifier
         "Effect": "Allow", // explicit allow/deny
         "Principal": 
            { "AWS":    "arn:aws:iam::123456789012:user/Alice" 
            }, // only for resource-based policies, who is allowed to do the action
         "Action": [
            "s3:ListBucket", 
            "s3:GetObject"
            ],
         "Resource": [
            "arn:aws:s3:::example_bucket",
            "arn:aws:s3:::example_bucket/*"
            ], // resources the action applies to, can use wildcards, * for all resources
        "Condition": {
            "IpAddress": { "aws:SourceIp": "10.0.0.0/16" }
        }
       }
     ]
   }
   ```
- Access Keys - programmatic access (no console access) to AWS services via CLI, SDKs, or APIs - consists of Access Key ID and Secret Access Key (for IaC tools like Terraform, CloudFormation, etc), keep them secret, Credential Report shows all users and their access key status (once per 4 hours)
- IAM Roles - similar to users but for AWS services or applications, can be assumed by trusted entities (users, services, accounts), temporary security credentials, used for cross-account access, EC2 instance profiles, Lambda execution roles, etc.
 - **No long-term credentials**, use STS to assume roles and get temporary credentials
 - Service-linked - trusted entity is an AWS service (e.g., EC2, Lambda)
 - Instance-linked 
 - trust policies define who can assume the role, example is:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": { "AWS": "arn:aws:iam::123456789012:user/Alice" },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ``` + permission policies define what actions are allowed when the role is assumed
   - Cross-account access - allow users from another AWS account to assume a role in your account, requires trust policy and permission policy
   - EC2 instance profiles - attach roles to EC2 instances for secure access to AWS services without hardcoding credentials - for example, an EC2 instance can assume a role to access S3 buckets securely

## VPC - Virtual Private Cloud
- logically isolated section of AWS cloud where you can launch AWS resources in a virtual network that you define - default VPC created in each region OR custom VPC
- VPC components:
 - CIDR Block - range of IP addresses for the VPC in IPv4 (e.g., 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
 - **Subnets** - segments of a VPC's IP address range where you can place groups of isolated resources, can be public (with internet access) or private (no direct internet access), VPN-only, or isolated
    - Every subnet get 5 reserved IP addresses (network address, VPC router, DNS server, future use, broadcast address)
    - Availability Zones - subnets are created in specific AZs for high availability (there is a **cost** for data transfer between AZs)
    - one route table per subnet
 - Route Tables - set of rules (routes) that determine where network traffic is directed, each subnet must be associated with a route table
   - Main Route Table - default route table for the VPC, automatically associated with all subnets unless explicitly associated with another route table
   - **Custom Route Tables** - can be created for specific routing needs (e.g., public/private subnets), need to associate subnets with custom route tables
   - Destination/Target/Local Route/Associations
    - Destination - CIDR block of the traffic
    - Target - where the traffic is directed (e.g., internet gateway, NAT gateway, VPC peering connection)
    - Local Route - automatically created route for communication within the VPC
    - Associations - link between a subnet and a route table
 - Security Groups - **stateful** (if inbound traffic is allowed, the response traffic is automatically allowed) virtual firewalls that control inbound and outbound traffic for AWS resources, stateful (return traffic is automatically allowed), EC2 level security, only allow rules (default deny all)
    - Can use anouther security group as a source/destination (reference by ID)
 - Network ACLs - **stateless** (no automatic allowance of return traffic) firewalls that control inbound and outbound traffic at the subnet level, more granular control than security groups, first match wins, one NACL per subnet
 - Internet Gateway - allows communication between instances in your VPC and the internet, needed for public subnets
 - Interface Endpoints - elastic network interfaces (ENIs) with private IP addresses that serve as entry points for traffic destined to supported AWS services, powered by AWS PrivateLink (more higher control than Gateway Endpoints)
 - NAT Gateway/Instance - allows instances in private subnets to access the internet for updates, etc., without exposing them to inbound internet traffic (it is using IP address of NAT Gateway), do not use security groups with NAT (just NACLs), **need to be in public subnet**
    - NAT - network address translation - translates private IP addresses to public IP addresses for outbound traffic
 - VPC Peering - connects two VPCs to route traffic between them using private IP addresses, can be within the same account or across different accounts (cross-account, cross-region), not-transitive -> you need to create peering connection (not overlaping CIDR), then update route tables, and adjust security groups/NACLs

### Notes
- Multi-tier architecture - separates application components into different layers (e.g., web, application, database) for better scalability, security, and manageability
- DHCP options set - configures network settings for instances in a VPC (e.g., DNS servers, NTP servers, domain name), once created it cannot be modified
- PrivateLink - allows private connectivity between VPCs and AWS services without using public IPs, uses interface endpoints (ENIs) in your VPC
- **Gateway Endpoint** - allows private connectivity to AWS services (only S3 or DynamoDB) without using public IPs, uses route tables to direct traffic to the endpoint, save money on data transfer costs, do not use security groups with Gateway Endpoints (just NACLs)
 - using prefix lists to allow access to multiple services in a single policy

## EC2 - Elastic Compute Cloud
- virtual servers in the cloud, can choose instance types, AMIs, storage options, networking, security settings
- Pay-as-you-go pricing model - pay for what you use (per second or per hour)
- Key Pairs - secure login information for EC2 instances, consists of a public key (stored in AWS) and a private key (downloaded by the user), use **SSH for Linux instances** - `ssh -i mykey.pem ec2-user@public-ip-address` 
- AMI - Amazon Machine Image - pre-configured templates for EC2 instances (OS, software, settings), can use AWS-provided, marketplace, or custom AMIs - public/private - good for prebaking common configurations
    - Can create custom AMIs from existing instances with your configurations (programs, files, settings, ...)
    - User data "booting" scrips - base64-encoded or shell scripts
- Class/Generation/Instance Size - T-family + Generation + size (t3.micro, t4g.large ...)
 - General Purpose - balanced CPU, memory, and networking (T, M, A families)
 - Compute Optimized - high CPU performance (C family)
 - Memory Optimized - high memory capacity (R, X, Z families)
 - Storage Optimized - high disk throughput and IOPS (I, D, H families)
 - Accelerated Computing - specialized hardware for ML, graphics, etc. (P, G, F families)
- You can hibernate the instance and continue later (RAM saved to EBS)
