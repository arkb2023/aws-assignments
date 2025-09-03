
---

# 📦 Module 2: Case Study - 1 (EC2-EBS-EFS)
## 📝 Tasks to Be Performed

1. Create an EC2 instance in the **US-East-1 (N. Virginia)** region with Linux OS and configure it as a web server using an AMI.
2. Replicate the instance in the **US-West-2 (Oregon)** region.
3. Build two EBS volumes and attach them to the instance in **US-East-1**.
4. Detach and delete one volume, then extend the size of the other.
5. Take a backup of the remaining EBS volume.

---

## ⚙️ Setup Steps

### 🚀 Create EC2 Instance in US-East-1
![Create EC2](images/WebserverNVirginia.png)

### 🔧 SSH into Instance and Install Nginx
![Install Nginx](images/NginxInstalledRunning.png)

### 🌐 Verify Web Server via Public DNS
![Nginx Webpage](images/NginxWebpageLoaded.png)

---

## 📸 Create AMI from EC2 Instance

### 🧱 Create Image
![Create Image](images/CreateImage.png)

### ✅ AMI Created
![AMI Created](images/AMICreated.png)

---

## 🌍 Replicate Instance in US-West-2 (Oregon)

### 📤 Copy AMI to Oregon
![Copy AMI](images/CopyAMI.png)  
![Copy to Oregon](images/CopyAMIToOregonRegion.png)

### 🔄 Switch Region and Verify AMI Availability
![AMI in Oregon](images/AMIAvailableInOregon.png)

---

## 💾 Manage EBS Volumes in US-East-1

### ➕ Create Two EBS Volumes
![Create Volumes](images/2VolumesCreated.png)

### 🔗 Attach Volumes to EC2 Instance
![Attach Volumes](images/AttachVolume.png)

#### 📎 Volume 1 Attached
![Attach Volume 1](images/AtttachVolume1ToEc2Instance.png)

#### 📎 Volume 2 Attached
![Attach Volume 2](images/AtttachVolume2ToEc2Instance.png)

---

## 🧪 Configure Volumes on Instance

### 🔍 Confirm Volumes via SSH
![Unmounted Volumes](images/UnmountedVolumesonInstance.png)

### 🧼 Format Disks
![Format Disks](images/formatDisks.png)

### 📂 Mount Volumes
![Mount Volumes](images/MountVolumes.png)

---

## 🧹 Detach and Delete Volume 2

### 🔌 Detach Volume 2
![Detach Volume 2](images/DetachVolume2.png)

### 🗑️ Delete Volume 2
![Delete Volume 2](images/DeleteVolume2.png)

---

## 📏 Resize Volume 1

### 🔧 Modify Volume from 10GB to 15GB
![Modify Volume](images/ModifyVolume1From10G-to-15G.png)

### 📊 Verify Resized Volume in Terminal
![Resized Volume](images/Volume1Resized.png)

---

## 🛡️ Backup Volume 1

### 📸 Create Snapshot
![Create Snapshot](images/CreateSnapShotOfVolume1.png)  
![Snapshot Step](images/CreateSnapShotOfVolume1-nextstep.png)

### ✅ Snapshot Completed
![Snapshot Completed](images/CompletedSnapshot.png)

---
