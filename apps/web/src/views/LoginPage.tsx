import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../auth/AuthContext';
import { AlertBanner } from '../components/AlertBanner';
import { APIError } from '../lib/api';

export function LoginPage() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      setLoading(false);
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (loading) return;
    setLoading(true);
    setErrorMessage('');
    try {
      await login(username, password);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      if (error instanceof APIError) {
        setErrorMessage(`${error.code}: ${error.message}`);
      } else {
        setErrorMessage('登录失败，请稍后重试。');
      }
      setLoading(false);
    }
  };

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="hero-panel__eyebrow">企业智能工作台</div>
        <h1>企业智能运营平台</h1>
        <p>
          面向销售、方案、采购、供应商与运营分析的一体化智能工作台，统一沉淀业务上下文、智能决策与执行闭环。
        </p>
        <div className="hero-panel__meta">
          <span>统一任务编排</span>
          <span>智能决策辅助</span>
          <span>可解释与可审计</span>
        </div>
        {errorMessage ? <AlertBanner title="登录失败" message={errorMessage} tone="danger" /> : null}
        <form className="page-stack" onSubmit={onSubmit}>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="用户名" />
          <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="密码" type="password" />
          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? '登录中...' : '进入工作台'}
          </button>
        </form>
        <div className="detail-block">
          <strong>默认演示账号</strong>
          <span>登录账号：admin</span>
          <span>登录密码：admin123</span>
        </div>
      </div>
    </div>
  );
}
