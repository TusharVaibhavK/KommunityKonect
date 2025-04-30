import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { scheduleService } from '../services/api';
import './Scheduler.css';

const Scheduler = () => {
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await scheduleService.createSchedule({ date, time });
      navigate('/services');
    } catch (err) {
      setError('Failed to schedule appointment');
    }
  };

  return (
    <div className="scheduler-container">
      <h2>Schedule Appointment</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Date</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Time</label>
          <input
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            required
          />
        </div>
        <button type="submit">Schedule</button>
      </form>
    </div>
  );
};

export default Scheduler;