import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { requestService } from '../services/api';
import './ServiceRequest.css';

const ServiceRequestCreate = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await requestService.createRequest({ title, description });
      navigate('/services');
    } catch (err) {
      setError('Failed to create service request');
    }
  };

  return (
    <div className="service-request-container">
      <h2>Create Service Request</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          ></textarea>
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default ServiceRequestCreate;