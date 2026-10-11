# BÁO CÁO KỸ THUẬT: PHÂN TÍCH KIẾN TRÚC CONTAINER VS VIRTUAL MACHINE
**Khóa học / Học phần:** IT_209 - Session 10: Containerization & Docker  
**Người thực hiện:** Sinh viên thực hành  
**Đường dẫn nộp bài:** `homework/session_10/ex1/`  
**Tệp đính kèm:** `REPORT.md`, `docker_info.png`, `docker_version.log`, `docker_info.log`

---

## 1. Bối cảnh Doanh nghiệp & Động lực Chuyển dịch từ VPS sang Docker

Trong hạ tầng công nghệ thông tin truyền thống, các doanh nghiệp thường triển khai các dịch vụ trên **Máy chủ ảo (VPS - Virtual Private Server)** hoặc máy chủ vật lý độc lập. Tuy nhiên, khi hệ thống mở rộng theo xu hướng Microservices và yêu cầu chu kỳ release tính năng liên tục (CI/CD), mô hình VPS bộc lộ nhiều điểm nghẽn nghiêm trọng:

1. **Lãng phí tài nguyên máy chủ (Resource Inefficiency):**  
   Mỗi VPS đều phải chạy một bản sao hệ điều hành khách (**Guest OS**) đầy đủ, kèm theo kernel riêng, các dịch vụ hệ thống chạy ngầm (`systemd`, logging daemons, kernel modules,...). Một VPS thông thường mất tối thiểu 1GB - 2GB RAM và hàng chục GB dung lượng đĩa chỉ để duy trì hệ điều hành, dù ứng dụng nghiệp vụ bên trong chỉ tiêu tốn vài chục MB RAM.
2. **Chi phí hạ tầng đám mây cao (High Cloud Infrastructure Cost):**  
   Doanh nghiệp phải mua nhiều gói VPS dung lượng cố định để cách ly các dịch vụ, dẫn đến hiện tượng cấp phát dư thừa (**Over-provisioning**), trong khi mức sử dụng CPU/RAM trung bình thực tế chỉ đạt 15% - 25%.
3. **Tốc độ triển khai và mở rộng chậm (Slow Deployment & Auto-scaling):**  
   Khởi động một VPS mới mất từ 1 đến 3 phút (boot firmware/UEFI, nạp kernel, mount filesystem, khởi tạo network). Điều này không đáp ứng được nhu cầu mở rộng quy mô tức thì (**horizontal auto-scaling**) khi lưu lượng truy cập tăng đột biến.
4. **Vấn đề môi trường không đồng nhất ("It works on my machine"):**  
   Việc cấu hình thủ công hoặc bằng script trên từng VPS dễ dẫn đến sai lệch phiên bản thư viện, biến môi trường giữa môi trường Dev, Staging và Production.

👉 **Giải pháp chuyển đổi sang Docker (Containerization):**  
Docker cung cấp giải pháp ảo hóa ở cấp độ hệ điều hành (**OS-level Virtualization**). Bằng cách dùng chung Kernel của máy chủ chủ (**Host Kernel**), Docker loại bỏ hoàn toàn tầng Guest OS nặng nề, cho phép đóng gói ứng dụng cùng đầy đủ thư viện phụ thuộc vào một **Container Image** gọn nhẹ, khởi động chỉ trong tích tắc, giúp doanh nghiệp tăng mật độ phục vụ trên cùng một máy chủ vật lý lên gấp 5 - 10 lần và tiết kiệm tới 40% - 60% chi phí hạ tầng.

---

## 2. Bảng So sánh Chuyên sâu: Virtual Machine (VPS) vs Container (Docker)

### 2.1. Sơ đồ Kiến trúc So sánh

```
┌──────────────────────────────────────┐     ┌──────────────────────────────────────┐
│        VIRTUAL MACHINE (VPS)         │     │          CONTAINER (DOCKER)          │
├──────────────────┬───────────────────┤     ├──────────────────┬───────────────────┤
│ App 1 + Libs     │ App 2 + Libs      │     │ App 1 + Libs     │ App 2 + Libs      │
├──────────────────┼───────────────────┤     ├──────────────────┴───────────────────┤
│ Guest OS (Linux) │ Guest OS (Ubuntu) │     │         Docker Engine / runc         │
├──────────────────┴───────────────────┤     ├──────────────────────────────────────┤
│  Hypervisor (KVM, VMware, Hyper-V)   │     │   Host OS Kernel (Linux / WSL2)      │
├──────────────────────────────────────┤     ├──────────────────────────────────────┤
│          Host OS / Hardware          │     │        Infrastructure / Hardware     │
└──────────────────────────────────────┘     └──────────────────────────────────────┘
```

### 2.2. Bảng Đối chiếu theo 5 Tiêu chí Trọng yếu

| Tiêu chí | Virtual Machine (VPS / Hypervisor) | Container (Docker Engine) | Phân tích Đánh giá Kỹ thuật |
| :--- | :--- | :--- | :--- |
| **1. Dung lượng Image** | **Rất lớn** (Thường từ vài GB đến hàng chục GB) | **Rất nhỏ** (Từ vài MB như Alpine ~5MB đến vài trăm MB) | VM Image phải chứa toàn bộ file hệ điều hành, kernel image, driver và file nhị phân. Docker image được xây dựng theo các tầng (**Layered Architecture / OverlayFS**), kế thừa và tái sử dụng layer, chỉ chứa mã nguồn ứng dụng và runtime cần thiết. |
| **2. Thời gian khởi động** | **Chậm** (Mất từ 30 giây đến vài phút) | **Tức thì** (Từ vài mili-giây đến 1-2 giây) | VM phải trải qua toàn bộ chu kỳ khởi động phần cứng ảo (Virtual BIOS/UEFI, nạp Kernel vào RAM, chạy tiến trình init `systemd`). Container thực chất chỉ là một tiến trình người dùng (**User-space Process**) được cô lập chạy trực tiếp trên Host Kernel đã khởi động sẵn. |
| **3. Hao phí OS (Overhead)** | **Cao** (Chiếm dụng 1 - 2 GB RAM và chu kỳ CPU cho mỗi Guest OS) | **Gần như bằng 0** (Chỉ tiêu hao tài nguyên cho chính ứng dụng) | Mỗi VPS chạy song song một bản kernel riêng và hàng chục tiến trình nền quản trị OS. Container không có Guest OS, không tiêu tốn RAM cho hệ điều hành ảo, mang lại hiệu suất thực thi gần như tương đương Bare-metal (Native performance). |
| **4. Mức độ cô lập (Isolation)** | **Cực kỳ cao** (Cô lập ở tầng phần cứng qua Hypervisor) | **Trung bình - Cao** (Cô lập ở tầng tiến trình hệ điều hành qua Namespaces & cgroups) | VM cô lập hoàn toàn phần cứng; lỗ hổng bảo mật ở một VM hầu như không thể xâm nhập sang VM khác. Container dùng chung Kernel, do đó nếu Kernel có lỗ hổng chưa vá (Kernel CVEs), kẻ tấn công có thể thực hiện tấn công leo thang đặc quyền (**Container Breakout**). |
| **5. Khả năng mở rộng (Scalability)** | **Kém linh hoạt, giới hạn mật độ** (Tốn nhiều tài nguyên khi scale ngang) | **Cực cao, tối ưu mật độ** (Scale tức thời, mật độ triển khai gấp 5 - 10 lần) | VM yêu cầu cấp phát cố định vCPU/vRAM, việc scale-out mất thời gian chờ boot máy ảo. Container cho phép co giãn linh hoạt theo giây (Kubernetes HPA), hỗ trợ triển khai hàng trăm container trên cùng một máy chủ vật lý. |

---

## 3. Cơ chế Cô lập Kernel (Namespaces) và Quản lý Tài nguyên (Control Groups - cgroups)

Container trong Linux thực chất không phải là một thực thể ảo hóa phần cứng độc lập, mà là **một tiến trình tiêu chuẩn trên Host được đóng gói và kiểm soát bởi hai cơ chế cốt lõi của Linux Kernel: Namespaces và Control Groups (cgroups)**.

### 3.1. Linux Namespaces - Cơ chế Cô lập Không gian Hoạt động (Virtual View Isolation)

Namespaces cung cấp cho tiến trình một góc nhìn ảo hóa riêng biệt về các tài nguyên của hệ điều hành, khiến tiến trình tưởng rằng nó đang sở hữu toàn bộ hệ thống độc lập:

1. **PID Namespace (Process ID Isolation):**
   - **Vai trò:** Cô lập cây phân cấp tiến trình (`process tree`).
   - **Cơ chế:** Khi một container được khởi tạo, tiến trình chính của ứng dụng bên trong container sẽ nhận `PID = 1` (đóng vai trò tiến trình gốc tương tự `init` hay `systemd`). Tuy nhiên, trên hệ điều hành Host, tiến trình này chỉ mang một PID thông thường (ví dụ: `PID 14258`).
   - **Tác dụng:** Tiến trình trong container không thể nhìn thấy, gửi tín hiệu (`kill`, `SIGTERM`) hay can thiệp vào các tiến trình của Host hoặc của các container lân cận.

2. **NET Namespace (Network Isolation):**
   - **Vai trò:** Cô lập toàn bộ ngăn xếp mạng (**Network Stack**).
   - **Cơ chế:** Mỗi container có giao diện mạng loopback (`lo`), card mạng ảo riêng (thường là một đầu của cặp `veth` kết nối với bridge `docker0`), bảng định tuyến riêng (`routing table`), bảng lọc gói tin (`iptables/nftables`) và không gian cổng mạng riêng.
   - **Tác dụng:** Hai container khác nhau có thể cùng lắng nghe trên cổng `80` hoặc `8080` mà không hề xảy ra xung đột cổng (Port conflict). Docker Engine sẽ ánh xạ cổng từ Host vào Container thông qua NAT/iptables (ví dụ: `-p 8081:80` và `-p 8082:80`).

3. **MNT Namespace (Mount Points & Filesystem Isolation):**
   - **Vai trò:** Cô lập hệ thống tệp và cây thư mục gắn kết (**Mount Points**).
   - **Cơ chế:** Kết hợp với kỹ thuật `chroot` hoặc lệnh hệ thống `pivot_root`, MNT namespace cho phép container chỉ nhìn thấy hệ thống tệp gốc (`rootfs`) của riêng nó (được cung cấp bởi Image thông qua Storage Driver `overlayfs`).
   - **Tác dụng:** Mọi thao tác tạo mới, sửa đổi, xóa tệp tin bên trong container diễn ra hoàn toàn biệt lập, không làm thay đổi các file hệ thống của máy chủ Host.

4. **Các Namespaces bổ trợ quan trọng khác:**
   - **IPC Namespace:** Cô lập cơ chế giao tiếp liên tiến trình (Inter-Process Communication: shared memory, POSIX message queues, semaphores).
   - **UTS Namespace:** Cho phép mỗi container sở hữu hostname và NIS domain riêng biệt mà không thay đổi hostname của Host.
   - **USER Namespace:** Ánh xạ UID/GID bên trong container ra ngoài Host (ví dụ: user `root` có UID 0 trong container tương ứng với một user không có đặc quyền UID 10001 ngoài Host), giúp giảm thiểu rủi ro bảo mật nếu xảy ra container breakout.

---

### 3.2. Control Groups (cgroups) - Cơ chế Phân bổ và Giới hạn Tài nguyên Vật lý

Nếu Namespaces trả lời câu hỏi *"Tiến trình được nhìn thấy những gì?"* thì cgroups giải quyết câu hỏi *"Tiến trình được phép sử dụng bao nhiêu tài nguyên?"*.

1. **Giới hạn và Phân bổ CPU (CPU Limits & Fair Scheduling):**
   - Sử dụng bộ lập lịch Linux CFS (**Completely Fair Scheduler**).
   - Tham số cấu hình: Docker cung cấp cờ `--cpus="1.5"` hoặc `--cpu-period` và `--cpu-quota`.
   - **Cơ chế:** Nếu chu kỳ thời gian là 100.000 µs (100ms) và hạn mức quota được đặt là 50.000 µs, container sẽ chỉ được phép chạy tối đa 50% thời gian CPU trong chu kỳ đó. Điều này ngăn chặn hiện tượng một container bị lỗi vòng lặp vô tận chiếm đoạt toàn bộ CPU của máy chủ (**Noisy Neighbor Problem**).

2. **Giới hạn Dung lượng Bộ nhớ RAM (Memory Limits & OOM Killer):**
   - Tham số cấu hình: Docker cung cấp cờ `-m` / `--memory="512m"` và `--memory-swap`.
   - **Cơ chế:** Kernel theo dõi chặt chẽ tổng dung lượng RAM (RSS, page cache) mà các tiến trình trong cgroup tiêu thụ.
   - **Bảo vệ hệ thống:** Khi container vượt quá ngưỡng bộ nhớ cho phép (`memory.max`), cơ chế **Out-Of-Memory (OOM) Killer** của Linux Kernel sẽ được kích hoạt để terminate tiến trình bên trong container vi phạm, hoàn toàn không làm gián đoạn hay sập hệ điều hành Host và các container khác.

3. **Kiểm soát Băng thông I/O và Giới hạn Số lượng Tiến trình (I/O & PID Limits):**
   - **BlkIO/I/O cgroup:** Điều chỉnh tốc độ đọc/ghi đĩa (`--device-read-bps`, `--device-write-bps`), đảm bảo một container không làm tắc nghẽn băng thông đĩa cứng.
   - **PIDs cgroup (`pids.max`):** Giới hạn số lượng tiến trình tối đa được tạo trong container, ngăn chặn hoàn toàn các cuộc tấn công kiểu Fork Bomb làm cạn kiệt bảng quản lý tiến trình của Kernel.

---

## 4. Thực nghiệm Trích xuất Thông số từ Lệnh `docker version` và `docker info`

Môi trường kiểm tra được thực hiện trực tiếp trên hệ thống cục bộ bằng tài khoản người dùng thông thường (`ADMIN` / PowerShell terminal không cần quyền nâng cao `sudo`).

### 4.1. Kết quả Lệnh Kiểm tra Phiên bản: `docker version`

```text
Client:
 Version:           29.7.2
 API version:       1.55
 Go version:        go1.26.5
 Git commit:        a7dcaa6
 Built:             Wed Aug  5 18:31:33 2026
 OS/Arch:           windows/amd64
 Context:           desktop-linux

Server: Docker Desktop 4.87.0 (236836)
 Engine:
  Version:          29.7.2
  API version:      1.55 (minimum version 1.40)
  Go version:       go1.26.5
  Git commit:       6a43e3d
  Built:            Wed Aug  5 18:28:36 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.2.5
  GitCommit:        e53c7c1516c3b2bff98eb76f1f4117477e6f4e66
 runc:
  Version:          1.3.6
  GitCommit:        v1.3.6-0-g491b69ba
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0
```

---

### 4.2. Bảng Trích xuất Thông số Cơ bản từ Lệnh `docker info`

Dưới đây là các thông số cốt lõi được trích xuất trực tiếp từ đầu ra của lệnh `docker info`:

| Thông số Yêu cầu | Giá trị Trích xuất từ Hệ thống | Ý nghĩa Kỹ thuật |
| :--- | :--- | :--- |
| **Server Version** | **29.7.2** (Docker Desktop 4.87.0) | Phiên bản Docker Daemon Engine đang phục vụ xử lý container. |
| **Cgroup Driver** | **cgroupfs** | Trình điều khiển quản lý cgroups trong Linux Kernel (hỗ trợ cgroups v2: `Cgroup Version: 2`). |
| **Số lượng Containers** | **2** (Running: 0, Paused: 0, Stopped: 2) | Tổng số container hiện có trên node máy chủ cục bộ. |
| **Số lượng Images** | **2** | Tổng số Container Images đã được tải hoặc build lưu tại local cache. |
| **Storage Driver** | **overlayfs** (`io.containerd.snapshotter.v1`) | Trình điều khiển lưu trữ đa tầng kết hợp UnionFS hiệu năng cao. |
| **Kernel Version** | **6.18.33.2-microsoft-standard-WSL2** | Phiên bản Linux Kernel máy chủ đang chia sẻ cho các container. |
| **Operating System** | **Docker Desktop** (WSL2 backend) | Môi trường hệ điều hành nền tảng cung cấp Docker runtime. |
| **Architecture** | **x86_64** | Kiến trúc CPU của hệ thống phần cứng. |
| **CPUs** | **16 vCPUs** | Tổng số luồng xử lý CPU mà Docker daemon nhận diện. |
| **Total Memory** | **7.601 GiB** | Tổng dung lượng RAM khả dụng được cấp phát cho Docker engine. |

> **Lệnh kiểm tra nhanh Cgroup Driver:**
> ```powershell
> docker info | Select-String -Pattern "cgroup"
> ```
> **Kết quả:**
> ```text
>  Cgroup Driver: cgroupfs
>  Cgroup Version: 2
>   cgroupns
> ```

---

### 4.3. Ảnh Chụp Minh chứng Terminal (Log lệnh `docker info`)

Minh chứng lệnh `docker info` thực thi đầy đủ trên hệ thống được lưu tại tệp hình ảnh đính kèm:  
`docker_info.png` *(Được lưu cùng thư mục báo cáo)*

---

## 5. Kết luận & Khuyến nghị Triển khai cho Doanh nghiệp

1. **Khuyến nghị Chuyển dịch:**  
   Đối với các ứng dụng nghiệp vụ dạng Stateless, Web APIs, Microservices và nền tảng kiểm thử CI/CD, doanh nghiệp nên chuyển đổi 100% từ mô hình VPS truyền thống sang Docker Container để tối đa hóa hiệu suất và giảm chi phí vận hành đám mây.
2. **Lưu ý về Bảo mật (Security Best Practices):**  
   Do Container chia sẻ chung Host Kernel:
   - Không chạy container dưới quyền `root` (sử dụng User Namespace hoặc cấu hình `USER nonroot` trong Dockerfile).
   - Thiết lập giới hạn tài nguyên định mức bằng cgroups (`--cpus`, `--memory`) cho toàn bộ container để tránh nguy cơ cạn kiệt tài nguyên hệ thống.
   - Thường xuyên quét lỗ hổng bảo mật của image định kỳ bằng công cụ như Docker Scout hoặc Trivy.

---
*Báo cáo được hoàn thành đầy đủ theo các tiêu chí và yêu cầu kỹ thuật của bài tập Session 10.*
