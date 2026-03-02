import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './HotTopics.css'

function StockTable({ stocks, type }) {
  if (stocks.length === 0) {
    return <p className="hot-empty">--</p>
  }

  return (
    <div className="hot-table-wrapper">
      <table className="hot-table">
        <thead>
          <tr>
            <th>代碼</th>
            <th>名稱</th>
            <th>收盤價</th>
            <th>{type === 'up' ? '漲幅' : '跌幅'}</th>
            <th>漲跌</th>
            <th>成交量</th>
            <th>市場</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((stock) => (
            <tr key={`${stock.market}-${stock.code}`}>
              <td className="hot-code">{stock.code}</td>
              <td>{stock.name}</td>
              <td className="hot-number">{stock.close_price.toFixed(2)}</td>
              <td className={`hot-number ${type === 'up' ? 'hot-up' : 'hot-down'}`}>
                {stock.change_percent > 0 ? '+' : ''}
                {stock.change_percent.toFixed(2)}%
              </td>
              <td className={`hot-number ${type === 'up' ? 'hot-up' : 'hot-down'}`}>
                {stock.change > 0 ? '+' : ''}
                {stock.change.toFixed(2)}
              </td>
              <td className="hot-number">
                {stock.volume.toLocaleString()}
              </td>
              <td>
                <span className={`hot-market-badge ${stock.market === 'TWSE' ? 'badge-twse' : 'badge-tpex'}`}>
                  {stock.market === 'TWSE' ? '上市' : '上櫃'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function HotTopics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dates, setDates] = useState([])
  const [selectedDate, setSelectedDate] = useState('')

  // 載入可用日期
  useEffect(() => {
    fetch('/api/hot-topics/dates?limit=60')
      .then((res) => res.json())
      .then((dateList) => {
        setDates(dateList)
      })
      .catch(() => {
        // 日期清單載入失敗不阻塞主要功能
      })
  }, [])

  // 載入漲跌停資料
  useEffect(() => {
    setLoading(true)
    setError(null)

    const url = selectedDate
      ? `/api/hot-topics?date=${selectedDate}`
      : '/api/hot-topics'

    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error('查詢失敗')
        return res.json()
      })
      .then((result) => {
        setData(result)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message || '載入資料失敗')
        setLoading(false)
      })
  }, [selectedDate])

  return (
    <div className="hot-topics">
      <header className="hot-header">
        <div className="hot-header-top">
          <Link to="/" className="hot-back-btn">
            ← 返回儀表板
          </Link>
          <h1 className="hot-title">熱門話題</h1>
        </div>
        <p className="hot-subtitle">今日漲停板與跌停板股票</p>
      </header>

      <div className="hot-controls">
        <label className="hot-date-label" htmlFor="date-select">
          交易日期：
        </label>
        <select
          id="date-select"
          className="hot-date-select"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        >
          <option value="">最近交易日</option>
          {dates.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
        {data && data.date && (
          <span className="hot-current-date">
            查詢日期：{data.date}
          </span>
        )}
      </div>

      {loading && <p className="hot-loading">載入中...</p>}

      {error && (
        <div className="hot-error">
          <p>載入失敗：{error}</p>
          <p className="hot-error-hint">請確認資料庫服務是否正常運作</p>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <section className="hot-section">
            <h2 className="hot-section-title hot-section-up">
              漲停板
              <span className="hot-count">{data.limit_up.length} 檔</span>
            </h2>
            <StockTable stocks={data.limit_up} type="up" />
          </section>

          <section className="hot-section">
            <h2 className="hot-section-title hot-section-down">
              跌停板
              <span className="hot-count">{data.limit_down.length} 檔</span>
            </h2>
            <StockTable stocks={data.limit_down} type="down" />
          </section>
        </>
      )}
    </div>
  )
}

export default HotTopics
