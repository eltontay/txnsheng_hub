import Head from 'next/head'

export default function Home() {
  return (
    <div className="container">
      <Head>
        <title>Txnsheng Hub</title>
        <meta name="description" content="Txnsheng's Information Hub" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="main">
        <h1 className="title">
          Welcome to Txnsheng Hub
        </h1>

        <p className="description">
          A comprehensive information hub for research, work, and insights.
        </p>

        <div className="grid">
          <a href="https://github.com/eltontay/txnsheng_hub" className="card">
            <h2>Repository &rarr;</h2>
            <p>Access the GitHub repository for all content and updates.</p>
          </a>

          <a href="https://t.me/txnsheng" className="card">
            <h2>Contact &rarr;</h2>
            <p>Get in touch for bot access and collaborations.</p>
          </a>

          <a href="/docs" className="card">
            <h2>Documentation &rarr;</h2>
            <p>Learn how to use the Telegram bot and contribute.</p>
          </a>
        </div>
      </main>

      <footer className="footer">
        <a href="https://twitter.com/txnsheng" target="_blank" rel="noopener noreferrer">
          @txnsheng
        </a>
      </footer>
    </div>
  )
} 