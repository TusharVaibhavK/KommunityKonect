import { Link } from 'react-router-dom';
import './Home.css'; // Optional: For styling

const Home = () => {
  return (
    <div className="home-container">
      <h1>Welcome to Repair Service Platform</h1>
      <p>Manage your repair requests and schedule appointments with ease.</p>
      <div className="home-links">
        <Link to="/services">
          <button>View Service Requests</button>
        </Link>
        <Link to="/scheduler">
          <button>Schedule Appointment</button>
        </Link>
      </div>
    </div>
  );
};

export default Home;