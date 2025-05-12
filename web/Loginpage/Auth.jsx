import React, { useEffect, useState } from 'react';
import { FaUser, FaEnvelope, FaLock } from 'react-icons/fa';
import { useNavigate, Link } from 'react-router-dom';
import './Auth.css';

function AuthPage({ setIsLoggedIn }) {
  const [isLogin, setIsLogin] = useState(true); // State to toggle between login and signup
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const navigate = useNavigate();

  // Add 'login-page' class to body on mount and remove on unmount
  useEffect(() => {
    document.body.classList.add('login-page');
    return () => {
      document.body.classList.remove('login-page');
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (isLogin) {
      // Simulate successful login
      if (username && password) {
        setIsLoggedIn(true);
        navigate('/dashboard'); // Redirect to Dashboard page
      }
    } else {
      // Simulate successful signup
      if (username && email && password && confirmPassword === password) {
        setIsLoggedIn(true);
        navigate('/dashboard'); // Redirect to Dashboard page
      } else {
        alert('Please check your inputs');
      }
    }
  };

  return (
    <div>
      {/* Use Link to navigate to the home page (Page1) */}
      <Link to="/">
        <img src="/src/assets/logo.png" alt="Logo" className="page-logo" />
      </Link>

      <div className="wrapper">
        <form onSubmit={handleSubmit}>
          <h1>{isLogin ? 'Login' : 'Sign Up'}</h1>

          <div className="input-box">
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <FaUser className="icon" />
          </div>

          {!isLogin && (
            <div className="input-box">
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <FaEnvelope className="icon" />
            </div>
          )}

          <div className="input-box">
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <FaLock className="icon" />
          </div>

          {!isLogin && (
            <div className="input-box">
              <input
                type="password"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <FaLock className="icon" />
            </div>
          )}

          {isLogin && (
            <div className="remember-forgot">
              <label>
                <input type="checkbox" />
                Remember me
              </label>
              <a href="/#">Forgot password?</a>
            </div>
          )}

          <button type="submit">{isLogin ? 'Login' : 'Register'}</button>

          <div className="toggle-link">
            <p>
              {isLogin
                ? "Don't have an account? "
                : 'Already have an account? '}
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  setIsLogin(!isLogin);
                }}
              >
                {isLogin ? 'Register' : 'Login'}
              </a>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AuthPage;
