#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空气数据HTTP服务
基于Flask的RESTful API服务,用于查询和展示air_quality.db中的空气数据
"""

from flask import Flask, request, jsonify, render_template_string
import sqlite3
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# 数据库路径
DB_PATH = '/Users/lizhiwei/workspace/test/air_quanlity_viewer/air_quality.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 返回字典格式而不是元组
    return conn

def dict_from_row(row):
    """将SQLite Row对象转换为字典"""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}

@app.route('/')
def index():
    """主页 - 显示数据概览"""
    try:
        conn = get_db_connection()
        
        # 获取总记录数
        total_records = conn.execute('SELECT COUNT(*) FROM air_quality').fetchone()[0]
        
        # 获取最新数据
        latest_data = conn.execute('''
            SELECT * FROM air_quality 
            ORDER BY timestamp DESC 
            LIMIT 5
        ''').fetchall()
        
        # 获取城市列表
        cities = conn.execute('''
            SELECT DISTINCT city, COUNT(*) as count 
            FROM air_quality 
            GROUP BY city
            ORDER BY city
        ''').fetchall()
        
        # 获取AQI统计
        aqi_stats = conn.execute('''
            SELECT 
                MIN(aqi) as min_aqi,
                MAX(aqi) as max_aqi,
                AVG(aqi) as avg_aqi,
                MIN(timestamp) as first_record,
                MAX(timestamp) as last_record
            FROM air_quality
            WHERE aqi IS NOT NULL
        ''').fetchone()
        
        conn.close()
        
        # 转换为字典格式
        latest_data_list = [dict_from_row(row) for row in latest_data]
        cities_list = [dict_from_row(row) for row in cities]
        aqi_stats_dict = dict_from_row(aqi_stats)
        
        template = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>空气质量数据查询系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #4a5568;
            margin-bottom: 5px;
        }
        
        .stat-label {
            color: #718096;
            font-size: 0.9em;
        }
        
        .section {
            background: white;
            margin-bottom: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .section-header {
            background: #4a5568;
            color: white;
            padding: 15px 20px;
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .section-content {
            padding: 20px;
        }
        
        .city-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .city-item {
            background: #e2e8f0;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .latest-data {
            overflow-x: auto;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th,
        .data-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .data-table th {
            background: #f7fafc;
            font-weight: 600;
            color: #4a5568;
        }
        
        .aqi-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .aqi-good { background: #c6f6d5; color: #22543d; }
        .aqi-moderate { background: #fef5e7; color: #b7791f; }
        .aqi-unhealthy-sensitive { background: #fed7d7; color: #c53030; }
        .aqi-unhealthy { background: #feb2b2; color: #c53030; }
        .aqi-very-unhealthy { background: #fc8181; color: #742a2a; }
        
        .api-links {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }
        
        .api-link {
            display: block;
            padding: 15px;
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            text-decoration: none;
            color: #4a5568;
            transition: all 0.3s;
        }
        
        .api-link:hover {
            border-color: #667eea;
            background: #e6fffa;
            color: #2d3748;
        }
        
        .api-method {
            font-weight: bold;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>空气质量数据查询系统</h1>
            <p>实时空气质量数据查询和统计</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ total_records }}</div>
                <div class="stat-label">总记录数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ cities_list|length }}</div>
                <div class="stat-label">城市数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ "%.0f" % aqi_stats_dict.avg_aqi if aqi_stats_dict.avg_aqi else 'N/A' }}</div>
                <div class="stat-label">平均AQI</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ aqi_stats_dict.max_aqi if aqi_stats_dict.max_aqi else 'N/A' }}</div>
                <div class="stat-label">最高AQI</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">城市分布</div>
            <div class="section-content">
                <div class="city-list">
                    {% for city in cities_list %}
                        <div class="city-item">
                            {{ city.city }} ({{ city.count }}条记录)
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">最新数据</div>
            <div class="section-content">
                <div class="latest-data">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>时间</th>
                                <th>城市</th>
                                <th>AQI</th>
                                <th>PM2.5</th>
                                <th>PM10</th>
                                <th>污染等级</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for record in latest_data_list %}
                            <tr>
                                <td>{{ record.timestamp }}</td>
                                <td>{{ record.city }}</td>
                                <td>{{ record.aqi if record.aqi else 'N/A' }}</td>
                                <td>{{ "%.1f" % record.pm25 if record.pm25 else 'N/A' }}</td>
                                <td>{{ "%.1f" % record.pm10 if record.pm10 else 'N/A' }}</td>
                                <td>
                                    <span class="aqi-badge aqi-moderate">{{ record.level if record.level else 'N/A' }}</span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-header">API接口</div>
            <div class="section-content">
                <p>以下是可用的API接口：</p>
                <div class="api-links">
                    <a href="/api/air-quality" class="api-link">
                        <div class="api-method">GET</div>
                        <div>/api/air-quality</div>
                        <div>获取所有空气质量数据</div>
                    </a>
                    <a href="/api/cities" class="api-link">
                        <div class="api-method">GET</div>
                        <div>/api/cities</div>
                        <div>获取所有城市列表</div>
                    </a>
                    <a href="/api/stats" class="api-link">
                        <div class="api-method">GET</div>
                        <div>/api/stats</div>
                        <div>获取统计信息</div>
                    </a>
                </div>
                <p style="margin-top: 15px; color: #718096;">
                    支持参数查询：?page=1&limit=10&city=城市名&min_aqi=50&max_aqi=100&start_date=2025-11-01&end_date=2025-11-06
                </p>
            </div>
        </div>
    </div>
</body>
</html>
        '''
        
        return render_template_string(template, 
                                   total_records=total_records,
                                   cities_list=cities_list,
                                   aqi_stats_dict=aqi_stats_dict,
                                   latest_data_list=latest_data_list)
        
    except Exception as e:
        return f"错误: {str(e)}", 500

@app.route('/api/air-quality')
def get_air_quality():
    """获取空气质量数据"""
    try:
        conn = get_db_connection()
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 50)), 100)  # 限制最大100条
        city = request.args.get('city')
        min_aqi = request.args.get('min_aqi', type=int)
        max_aqi = request.args.get('max_aqi', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        where_conditions = []
        params = []
        
        if city:
            where_conditions.append("city LIKE ?")
            params.append(f"%{city}%")
            
        if min_aqi is not None:
            where_conditions.append("aqi >= ?")
            params.append(min_aqi)
            
        if max_aqi is not None:
            where_conditions.append("aqi <= ?")
            params.append(max_aqi)
            
        if start_date:
            where_conditions.append("DATE(timestamp) >= ?")
            params.append(start_date)
            
        if end_date:
            where_conditions.append("DATE(timestamp) <= ?")
            params.append(end_date)
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 获取总数
        total_count_query = f"SELECT COUNT(*) FROM air_quality {where_clause}"
        total_count = conn.execute(total_count_query, params).fetchone()[0]
        
        # 获取分页数据
        offset = (page - 1) * limit
        data_query = f'''
            SELECT * FROM air_quality 
            {where_clause}
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        '''
        data_params = params + [limit, offset]
        data = conn.execute(data_query, data_params).fetchall()
        
        conn.close()
        
        # 转换为字典格式
        data_list = [dict_from_row(row) for row in data]
        
        response = {
            "data": data_list,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            },
            "filters": {
                "city": city,
                "min_aqi": min_aqi,
                "max_aqi": max_aqi,
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/air-quality/<int:record_id>')
def get_air_quality_by_id(record_id):
    """获取特定ID的空气质量记录"""
    try:
        conn = get_db_connection()
        record = conn.execute('SELECT * FROM air_quality WHERE id = ?', (record_id,)).fetchone()
        conn.close()
        
        if record is None:
            return jsonify({"error": "记录不存在"}), 404
        
        return jsonify({"data": dict_from_row(record)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cities')
def get_cities():
    """获取所有城市列表"""
    try:
        conn = get_db_connection()
        cities = conn.execute('''
            SELECT city, 
                   COUNT(*) as record_count,
                   MIN(aqi) as min_aqi,
                   MAX(aqi) as max_aqi,
                   AVG(aqi) as avg_aqi
            FROM air_quality 
            GROUP BY city 
            ORDER BY city
        ''').fetchall()
        conn.close()
        
        cities_list = [dict_from_row(row) for row in cities]
        
        return jsonify({"data": cities_list})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """获取统计信息"""
    try:
        conn = get_db_connection()
        
        # 总记录数
        total_records = conn.execute('SELECT COUNT(*) FROM air_quality').fetchone()[0]
        
        # AQI统计
        aqi_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_records,
                MIN(aqi) as min_aqi,
                MAX(aqi) as max_aqi,
                AVG(aqi) as avg_aqi,
                MIN(timestamp) as first_record,
                MAX(timestamp) as last_record
            FROM air_quality
            WHERE aqi IS NOT NULL
        ''').fetchone()
        
        # 污染等级统计
        level_stats = conn.execute('''
            SELECT level, COUNT(*) as count
            FROM air_quality 
            WHERE level IS NOT NULL
            GROUP BY level
            ORDER BY count DESC
        ''').fetchall()
        
        # 最近数据趋势（最近7天）
        trend_data = conn.execute('''
            SELECT 
                DATE(timestamp) as date,
                AVG(aqi) as avg_aqi,
                COUNT(*) as record_count
            FROM air_quality 
            WHERE timestamp >= date('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        ''').fetchall()
        
        conn.close()
        
        stats = {
            "total_records": total_records,
            "aqi_stats": dict_from_row(aqi_stats),
            "level_distribution": [dict_from_row(row) for row in level_stats],
            "trend_data": [dict_from_row(row) for row in trend_data]
        }
        
        return jsonify({"data": stats})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    try:
        conn = get_db_connection()
        conn.execute('SELECT 1').fetchone()
        conn.close()
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"错误：数据库文件 {DB_PATH} 不存在")
        exit(1)
    
    start_port = 5001
    print("启动空气数据HTTP服务...")
    print(f"服务地址: http://localhost:{start_port}")
    print(f"API文档: http://localhost:{start_port}")
    
    app.run(debug=True, host='0.0.0.0', port=start_port)
