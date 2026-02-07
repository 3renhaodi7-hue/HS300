from fastapi import FastAPI
from mangum import Mangum
import akshare as ak
import pandas as pd
from datetime import datetime

app = FastAPI()

@app.get("/api/stockdata")
async def get_stock_data(days: int = 30):
    try:
        # 1. 获取沪深300指数数据 (注意：akshare 1.16.x 的函数名可能已变更)
        # 如果下一行报错，我们可能需要查找新版本对应的函数名
        index_data = ak.index_value_hist_funddb(symbol="沪深300")
        index_data['日期'] = pd.to_datetime(index_data['日期'])
        index_data = index_data.sort_values('日期').tail(days)

        # 2. 获取10年期国债收益率 (此函数名在近期版本中相对稳定)
        bond_yield_df = ak.bond_china_yield()
        bond_10y = bond_yield_df[bond_yield_df['期限'] == '10年'].copy()
        bond_10y['日期'] = pd.to_datetime(bond_10y['日期'])
        bond_10y = bond_10y.sort_values('日期').tail(days)

        # 3. 合并数据
        merged_df = pd.merge(
            index_data[['日期', '收盘', '市盈率']],
            bond_10y[['日期', '收益率']],
            on='日期',
            how='inner'
        )

        # 4. 格式化返回
        result = merged_df.to_dict(orient='records')
        return {
            "code": 200,
            "data": result,
            "message": "success"
        }

    except Exception as e:
        # 如果是因为函数名变更导致的错误，这里会捕获
        return {
            "code": 500,
            "data": None,
            "message": f"数据获取失败，可能是akshare接口已更新。错误详情: {str(e)}"
        }

# Netlify 函数入口
handler = Mangum(app)
