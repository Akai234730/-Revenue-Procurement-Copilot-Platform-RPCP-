import { NavLink } from 'react-router-dom';
import type { PropsWithChildren } from 'react';

import { useAuth } from '../auth/AuthContext';

const navItems = [
  { to: '/dashboard', label: '首页工作台' },
  { to: '/leads', label: '销售智能体' },
  { to: '/proposals', label: '方案智能体' },
  { to: '/procurement', label: '采购智能体' },
  { to: '/suppliers', label: '供应商智能体' },
  { to: '/knowledge', label: '知识中心' },
  { to: '/operations', label: '运营中心' },
  { to: '/settings', label: '系统设置' },
];

export function AppShell({ children }: PropsWithChildren) {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-badge">RPCP</div>
          <div>
            <h1>企业智能运营平台</h1>
            <p>销售协同 · 采购协同 · 知识管理 · 运营分析</p>
          </div>
        </div>

        <div className="detail-block">
          <strong>统一智能体工作台</strong>
          <span>面向销售、采购、供应商与经营分析的一体化 AI 协同平台。</span>
        </div>

        <nav className="nav-list">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? 'nav-item active' : 'nav-item')}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="detail-block">
          <strong>平台能力</strong>
          <span>可解释、可审计、可执行，支持统一任务编排与全链路观测。</span>
        </div>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <div>
            <strong>企业智能运营工作台</strong>
            <span className="muted">统一视图、统一上下文、统一执行链路</span>
          </div>
          <div className="topbar-actions">
            <button className="ghost-btn">全局搜索</button>
            <button className="ghost-btn">待审批 4</button>
            <span className="ghost-btn">{user?.name ?? '未登录'}</span>
            <button className="primary-btn" onClick={logout}>退出登录</button>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
