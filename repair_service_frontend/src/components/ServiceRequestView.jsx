import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { requestService } from '../services/api';
import './ServiceRequest.css';

const ServiceRequestView = () => {
  const { id } = useParams();
  const [request, setRequest] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRequest = async () => {
      try {
        const response = await requestService.getRequest(id);
        setRequest(response.data); // Assumes response.data is the request object
      } catch (err) {
        setError('Failed to fetch service request');
      }
    };
    fetchRequest();
  }, [id]);

  if (!request) return <div>Loading...</div>;

  return (
    <div className="service-request-container">
      <h2>{request.title}</h2>
      {error && <p className="error">{error}</p>}
      <p><strong>Description:</strong> {request.description}</p>
      <p><strong>Status:</strong> {request.status}</p>
    </div>
  );
};

export default ServiceRequestView;