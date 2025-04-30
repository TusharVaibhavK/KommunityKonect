import { useEffect, useState } from 'react';
import { requestService } from '../services/api';
import { Link } from 'react-router-dom';
import './ServiceRequest.css';

const ServiceRequestList = () => {
  const [requests, setRequests] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRequests = async () => {
      try {
        const response = await requestService.getAllRequests();
        setRequests(response.data); // Assumes response.data is the array of requests
      } catch (err) {
        setError('Failed to fetch service requests');
      }
    };
    fetchRequests();
  }, []);

  return (
    <div className="service-request-container">
      <h2>Service Requests</h2>
      <Link to="/services/new">
        <button>Create New Request</button>
      </Link>
      {error && <p className="error">{error}</p>}
      <ul className="request-list">
        {requests.map((request) => (
          <li key={request.id}>
            <Link to={`/services/${request.id}`}>
              {request.title} - {request.status}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ServiceRequestList;