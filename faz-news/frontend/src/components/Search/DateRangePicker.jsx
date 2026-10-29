import React, { useState } from 'react'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'

export default function DateRangePicker({ onRangeChange }) {
  const [startDate, setStartDate] = useState(null)
  const [endDate, setEndDate] = useState(null)

  const handleApply = () => {
    onRangeChange({ start: startDate, end: endDate })
  }

  const handleClear = () => {
    setStartDate(null)
    setEndDate(null)
    onRangeChange({ start: null, end: null })
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-3">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
          <DatePicker
            selected={startDate}
            onChange={setStartDate}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            placeholderText="Start date"
            className="input-field"
            dateFormat="MMMM d, yyyy"
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
          <DatePicker
            selected={endDate}
            onChange={setEndDate}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            placeholderText="End date"
            className="input-field"
            dateFormat="MMMM d, yyyy"
          />
        </div>
      </div>
      
      <div className="flex gap-2">
        <button onClick={handleApply} className="btn-primary flex-1">
          Apply Filter
        </button>
        <button onClick={handleClear} className="btn-secondary">
          Clear
        </button>
      </div>
      
      <div className="flex gap-2 pt-2">
        <button
          onClick={() => {
            const today = new Date()
            const weekAgo = new Date(today.setDate(today.getDate() - 7))
            setStartDate(weekAgo)
            setEndDate(new Date())
            onRangeChange({ start: weekAgo, end: new Date() })
          }}
          className="text-xs px-3 py-1 bg-gray-100 rounded-full hover:bg-gray-200"
        >
          Last 7 days
        </button>
        <button
          onClick={() => {
            const today = new Date()
            const monthAgo = new Date(today.setMonth(today.getMonth() - 1))
            setStartDate(monthAgo)
            setEndDate(new Date())
            onRangeChange({ start: monthAgo, end: new Date() })
          }}
          className="text-xs px-3 py-1 bg-gray-100 rounded-full hover:bg-gray-200"
        >
          Last 30 days
        </button>
      </div>
    </div>
  )
}