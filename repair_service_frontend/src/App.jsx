import { AuthProvider } from './contexts/AuthContext';
import Navigation from './components/Navigation';
import Home from './components/Home';
import './App.css';
import Login from './components/Login';
import Register from './components/Register';
import Scheduler from './components/Scheduler';
import ServiceRequestList from './components/ServiceRequestList';
import ServiceRequestCreate from './components/ServiceRequestCreate';

function App() {
  return (
    <AuthProvider>
      <div className="app-container">
        <Navigation />
        <main>
          <Login />
        </main>
      </div>
    </AuthProvider>
  );
}

export default App;