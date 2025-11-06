# 空气质量数据HTTP服务

基于Flask的RESTful API服务，用于查询和展示air_quality.db中的空气质量数据。

## 项目概述

本项目提供了一个完整的HTTP服务，让用户能够通过Web界面和API接口查看成都地区的空气质量数据。服务基于Python Flask框架开发，数据库使用SQLite，包含37条成都的空气质量记录。

## 快速开始

### 环境要求
- Python 3.7+
- Flask
- SQLite3

### 安装依赖
```bash
pip install flask
```

### 启动服务
```bash
python app.py
```

服务将在 `http://localhost:5001` 启动（注意：由于端口5000被占用，使用了5001端口）

## 功能特性

### Web界面
- **主页展示**: 实时数据概览、统计信息、城市分布
- **响应式设计**: 适配桌面和移动设备
- **美观界面**: 现代化的UI设计

### API接口
本服务提供以下RESTful API接口：

#### 1. 健康检查
- **URL**: `GET /api/health`
- **说明**: 检查服务状态
- **响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T16:35:23.065324"
}
```

#### 2. 获取所有城市列表
- **URL**: `GET /api/cities`
- **说明**: 获取所有城市及其统计信息
- **响应示例**:
```json
{
  "data": [
    {
      "city": "Chengdu (成都)",
      "record_count": 37,
      "min_aqi": 46,
      "max_aqi": 142,
      "avg_aqi": 85.84
    }
  ]
}
```

#### 3. 获取空气质量数据
- **URL**: `GET /api/air-quality`
- **说明**: 获取所有空气质量数据，支持分页和过滤
- **查询参数**:
  - `page`: 页码（默认1）
  - `limit`: 每页数量（默认50，最大100）
  - `city`: 城市名称过滤
  - `min_aqi`: AQI最小值过滤
  - `max_aqi`: AQI最大值过滤
  - `start_date`: 开始日期 (YYYY-MM-DD)
  - `end_date`: 结束日期 (YYYY-MM-DD)

- **响应示例**:
```json
{
  "data": [
    {
      "id": 3,
      "timestamp": "2025-11-04 03:30:21",
      "city": "Chengdu (成都)",
      "aqi": 46,
      "pm25": 46.0,
      "pm10": 29.0,
      "co": 4.6,
      "no2": 8.7,
      "o3": 0.0,
      "so2": 2.1,
      "level": "优",
      "source": "waqi",
      "raw_data": "..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 37,
    "pages": 1
  },
  "filters": {
    "city": null,
    "min_aqi": null,
    "max_aqi": null,
    "start_date": null,
    "end_date": null
  }
}
```

#### 4. 获取特定记录
- **URL**: `GET /api/air-quality/<id>`
- **说明**: 根据ID获取特定空气质量记录
- **响应示例**:
```json
{
  "data": {
    "id": 3,
    "timestamp": "2025-11-04 03:30:21",
    "city": "Chengdu (成都)",
    "aqi": 46,
    "pm25": 46.0,
    "pm10": 29.0,
    "co": 4.6,
    "no2": 8.7,
    "o3": 0.0,
    "so2": 2.1,
    "level": "优",
    "source": "waqi",
    "raw_data": "..."
  }
}
```

#### 5. 获取统计信息
- **URL**: `GET /api/stats`
- **说明**: 获取整体统计信息
- **响应示例**:
```json
{
  "data": {
    "total_records": 37,
    "aqi_stats": {
      "total_records": 37,
      "min_aqi": 46,
      "max_aqi": 142,
      "avg_aqi": 85.84,
      "first_record": "2025-11-04 03:30:21",
      "last_record": "2025-11-05 04:00:56"
    },
    "level_distribution": [
      {"level": "优", "count": 1},
      {"level": "良", "count": 1},
      {"level": "轻度污染", "count": 1}
    ],
    "trend_data": [...]
  }
}
```

## 数据库结构

### air_quality表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| timestamp | DATETIME | 时间戳 |
| city | TEXT | 城市名称 |
| aqi | INTEGER | 空气质量指数 |
| pm25 | REAL | PM2.5浓度 |
| pm10 | REAL | PM10浓度 |
| co | REAL | 一氧化碳浓度 |
| no2 | REAL | 二氧化氮浓度 |
| o3 | REAL | 臭氧浓度 |
| so2 | REAL | 二氧化硫浓度 |
| level | TEXT | 污染等级 |
| source | TEXT | 数据源 |
| raw_data | TEXT | 原始JSON数据 |

## 使用示例

### Web界面访问
直接访问 `http://localhost:5001` 查看数据概览

### API调用示例

```bash
# 获取健康状态
curl http://localhost:5001/api/health

# 获取城市列表
curl http://localhost:5001/api/cities

# 获取前10条数据
curl "http://localhost:5001/api/air-quality?limit=10"

# 获取成都的数据
curl "http://localhost:5001/api/air-quality?city=成都"

# 获取AQI在50-100之间的数据
curl "http://localhost:5001/api/air-quality?min_aqi=50&max_aqi=100"

# 获取特定日期范围的数据
curl "http://localhost:5001/api/air-quality?start_date=2025-11-01&end_date=2025-11-06"

# 获取第2页数据（每页20条）
curl "http://localhost:5001/api/air-quality?page=2&limit=20"
```

## 技术实现

### 后端技术
- **Flask**: Web框架
- **SQLite3**: 数据库
- **Python标准库**: 数据处理

### 前端技术
- **HTML5**: 页面结构
- **CSS3**: 样式设计（渐变背景、响应式布局）
- **Jinja2**: 模板引擎

### 核心功能
- **RESTful API设计**: 标准的REST接口
- **分页查询**: 支持大数据量分页
- **多条件过滤**: 灵活的数据筛选
- **数据统计**: AQI统计、趋势分析
- **错误处理**: 完善的异常处理机制

## 项目结构

```
air_quanlity_viewer/
├── app.py                 # 主应用文件
├── air_quality.db        # SQLite数据库
├── todo.md              # 任务清单
└── README.md            # 使用说明
```

## 部署说明

### 生产环境部署
1. 使用WSGI服务器（如Gunicorn）替代Flask开发服务器
2. 配置反向代理（如Nginx）
3. 设置数据库备份策略
4. 配置日志记录

### 性能优化
- 考虑添加Redis缓存
- 数据库索引优化
- API响应压缩

## 故障排除

### 常见问题
1. **端口占用**: 默认使用5001端口，如被占用请修改端口号
2. **数据库文件不存在**: 确保air_quality.db文件在正确位置
3. **Flask未安装**: 使用`pip install flask`安装依赖

### 日志查看
服务运行时会输出访问日志和错误信息，请关注控制台输出。

## 许可证

本项目仅供学习和演示使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址: `/Users/lizhiwei/workspace/test/air_quanlity_viewer`
- 服务地址: `http://localhost:5001`

---
*最后更新: 2025-11-06*
