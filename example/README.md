# FASTQ 测试文件说明

本目录包含用于测试 GSA FASTQ 验证器的示例文件。

## 文件列表

### 标准正确的文件

这些文件符合 GSA 提交要求，应该通过所有验证检查：

| 文件名 | 说明 |
|--------|------|
| `sample_correct.fastq` | 未压缩的标准 FASTQ 文件 |
| `sample_correct.fastq.gz` | gzip 压缩的标准 FASTQ 文件 |
| `sample_correct.fastq.bz2` | bzip2 压缩的标准 FASTQ 文件 |
| `sample_paired_1.fastq.gz` | 配对读取 R1（使用 `_1` 后缀） |
| `sample_paired_2.fastq.gz` | 配对读取 R2（使用 `_2` 后缀） |
| `sample_phred64.fastq.gz` | Phred 64 格式（用于测试自动检测） |

### 真实测试数据（从 ENA 下载）

这些是从 ENA (European Nucleotide Archive) 下载的真实 FASTQ 文件，用于更真实的测试场景：

| 文件名 | 说明 | 数据来源 |
|--------|------|---------|
| `ERR10064847_1.fastq.gz` | 真实配对读取 R1（88,118 个读取，2.7 MB） | ENA: ERR10064847 |
| `ERR10064847_2.fastq.gz` | 真实配对读取 R2（88,118 个读取，3.2 MB） | ENA: ERR10064847 |

**注意**：这些是真实的测序数据文件，文件较大，适合用于：
- 测试工具在真实数据上的性能
- 验证配对文件匹配功能
- 测试批量处理功能

### BAM 测试文件

| 文件名 | 说明 | 数据来源 |
|--------|------|---------|
| `test_sample.bam` | 小样本BAM文件（1000条reads，94 KB） 

### 错误文件（用于测试验证器）

这些文件包含各种错误，用于测试验证器是否能正确识别问题：

| 文件名 | 错误类型 | 预期错误信息 |
|--------|---------|-------------|
| `error_missing_at.fastq.gz` | 读取标识符不以 `@` 开头 | 标识符行格式错误 |
| `error_wrong_structure.fastq.gz` | FASTQ 结构不正确（不是4行/读取） | FASTQ 结构错误 |
| `error_invalid_base.fastq.gz` | 包含无效碱基字符（XYZ） | 碱基序列格式错误 |
| `error_quality_mismatch.fastq.gz` | 质量评分行长度与序列行不匹配 | 质量评分长度不匹配 |
| `error_missing_plus.fastq.gz` | 分隔符行不以 `+` 开头 | 分隔符行格式错误 |
| `error_empty.fastq.gz` | 空文件 | 文件为空 |
| `error_wrong_compression.fastq.zip` | 不支持的压缩格式（.zip） | 压缩格式不符合要求 |

## 注意事项

⚠️ **文件名格式说明**：
- 当前验证器实现禁止文件名中包含句点（`.`），包括文件扩展名中的句点
- 根据 GSA 实际要求，文件扩展名中的句点应该是允许的（如 `sample.fastq.gz`）
- 测试文件使用标准格式 `filename.fastq.gz`，但验证器会报告文件名格式错误
- 这是验证器的一个已知限制，实际 GSA 提交时可以使用句点

## 下载真实 FASTQ 文件

### 从 ENA 下载文件

你可以使用 `curl` 从 ENA 下载 FASTQ 文件：

```bash
# 方法1：使用 ENA API 查询下载链接
curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=ERR10064847&result=read_run&fields=fastq_ftp"

# 方法2：直接使用 HTTP 下载（推荐）
# 配对文件 ERR10064847（已下载到本目录）
curl -L -o ERR10064847_1.fastq.gz "https://ftp.sra.ebi.ac.uk/vol1/fastq/ERR100/047/ERR10064847/ERR10064847_1.fastq.gz"
curl -L -o ERR10064847_2.fastq.gz "https://ftp.sra.ebi.ac.uk/vol1/fastq/ERR100/047/ERR10064847/ERR10064847_2.fastq.gz"

# 下载单端文件示例
curl -L -o ERR2676781.fastq.gz "https://ftp.sra.ebi.ac.uk/vol1/fastq/ERR267/678/ERR2676781/ERR2676781.fastq.gz"
```

**提示**：
- ENA 的路径格式为 `vol1/fastq/{前6位}/{后3位}/{完整编号}/`
- 使用 HTTPS 协议（`https://ftp.sra.ebi.ac.uk/`）比 FTP 更可靠
- 可以使用 ENA API 查询正确的下载路径

### 验证配对文件

```bash
# 从 example 目录运行
cd example

# 验证真实配对文件 ERR10064847
python validate_paired_files.py ERR10064847_1.fastq.gz ERR10064847_2.fastq.gz

# 验证示例配对文件
python validate_paired_files.py sample_paired_1.fastq.gz sample_paired_2.fastq.gz

# 或从项目根目录运行
python example/validate_paired_files.py example/ERR10064847_1.fastq.gz example/ERR10064847_2.fastq.gz
```

**验证内容**：
- ✅ 读取数量匹配
- ✅ 读取ID匹配（去除配对标识后）
- ✅ 文件大小合理

**示例输出（ERR10064847）**：
```
📊 统计读取数量...
  文件1读取数: 88,118
  文件2读取数: 88,118
  ✓ 读取数量匹配

🔍 检查读取ID匹配（检查前 1000 个读取）...
  ✓ 所有检查的读取ID都匹配

📦 文件大小:
  文件1: 2.73 MB
  文件2: 3.16 MB
  大小比例: 1.16x
  ✓ 文件大小比例合理

✓ 配对文件验证通过！
```

## 使用方法

### 1. 测试标准文件

```bash
# 从项目根目录运行
cd /path/to/gsa_fastq_validator

# 测试单个文件
python gsa_validator.py example/sample_correct.fastq.gz

# 测试所有标准文件
python gsa_validator.py example/sample_correct.fastq.gz --verbose
python gsa_validator.py example/sample_correct.fastq.bz2 --verbose
python gsa_validator.py example/sample_paired_1.fastq.gz --verbose
```

### 2. 测试错误文件

```bash
# 从项目根目录运行
cd /path/to/gsa_fastq_validator

# 测试各种错误类型
python gsa_validator.py example/error_missing_at.fastq.gz --verbose
python gsa_validator.py example/error_invalid_base.fastq.gz --verbose
python gsa_validator.py example/error_quality_mismatch.fastq.gz --verbose
```

### 3. 批量测试

```bash
# 从项目根目录运行
cd /path/to/gsa_fastq_validator

# 批量测试 example 目录中的所有文件
python gsa_validator.py --batch example --verbose

# 只测试 .gz 文件
python gsa_validator.py --batch example --pattern "*.gz" --verbose
```

### 4. 生成和验证 MD5

```bash
# 从项目根目录运行
cd /path/to/gsa_fastq_validator

# 生成 MD5 校验码
python gsa_validator.py example/sample_correct.fastq.gz --generate-md5

# 验证 MD5 校验码
python gsa_validator.py example/sample_correct.fastq.gz --verify-md5
```

### 5. 测试BAM文件

```bash
# 从项目根目录运行
cd /path/to/gsa_fastq_validator

# 测试BAM文件
python gsa_validator.py example/test_sample.bam

# 测试完整BAM文件（较大）
python gsa_validator.py example/NA12878.chrom20.bam
```

### 6. 使用测试脚本

运行提供的测试脚本：

```bash
python example/test_examples.py
```

## 重新生成测试文件

如果需要重新生成测试文件，运行：

```bash
# 生成FASTQ测试文件
python example/generate_test_files.py

# 从完整BAM文件提取小样本
python example/extract_small_bam.py NA12878.chrom20.bam test_sample.bam 1000
```

## 文件格式说明

### FASTQ 格式

每个读取包含4行：

```
@read_identifier/1
ATCGATCGATCG...
+
IIIIIIIIIIII...
```

1. **读取标识符行**：以 `@` 开头
2. **碱基序列行**：仅包含 `A`, `C`, `G`, `T`, `N`（大小写均可）和 `.`
3. **分隔符行**：以 `+` 开头（可选包含读取标识符）
4. **质量评分行**：与序列行长度相同的 ASCII 字符（Phred 33 或 64）

### GSA 要求

- **文件扩展名**：`.fastq` 或 `.fq`
- **压缩格式**：仅接受 `.gz` (gzip) 或 `.bz2` (bzip2)
- **文件命名**：不能包含空格、连字符、括号、句点或正反斜杠
- **配对读取**：使用 `_1`/`_2` 或 `R1`/`R2` 后缀

## 参考

- [GSA 官方提交指南](https://ngdc.cncb.ac.cn/gsa/document/GSA-GSA_Submission_Guide_2.3.cn.pdf)
- [GSA 标准页面](https://ngdc.cncb.ac.cn/gsa/support/standardsGsa)
