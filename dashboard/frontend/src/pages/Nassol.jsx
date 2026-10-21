import React, { useState } from 'react'

const SAMPLE = {
  person: '28기 영자·영철',
  title: '나는솔로 28기 영자·영철 결별, 혼인신고 안 했다는 말이 더 눈에 들어왔다',
  sources: [{ date: '2026-07-31', claim: '공개 보도에 따르면 두 사람은 관계를 정리했다고 전해졌다.', url: 'https://v.daum.net/v/20260731172928721' }],
  editorial: { hook: '방송에서 이어진 관계의 근황을 다시 봤음.', take: '내가 주목한 건 결혼식과 혼인신고가 별개의 절차라는 점임. 속사정은 단정할 수 없음.', ending: '방송 속 결말과 현실의 관계는 다를 수 있다고 생각함.' },
  profile: { 방송: '나는 SOLO 28기' }
}

export default function Nassol() {
  const [raw, setRaw] = useState(JSON.stringify(SAMPLE, null, 2))
  const [draft, setDraft] = useState('')
  const [title, setTitle] = useState('')
  const [media, setMedia] = useState({cards: [], video: null, media_error: null})
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function generate() {
    setError(''); setBusy(true)
    try {
      const body = JSON.parse(raw)
      const response = await fetch('/api/nassol/draft', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      const data = await response.json()
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
      setDraft(data.draft); setTitle(data.title); setMedia({cards: data.cards || [], video: data.video, media_error: data.media_error})
    } catch (e) { setError(String(e.message || e)) }
    finally { setBusy(false) }
  }
  return <div className="p-6 max-w-5xl mx-auto space-y-4">
    <h1 className="text-xl font-bold">나는 SOLO · 원고 검수</h1>
    <p className="text-sm text-subtext">검증된 기사 내용과 직접 작성한 관점을 JSON에 입력하세요. 최종 제목은 1개만 생성합니다. 샘플 내용은 실제 기사 검증이 완료된 데이터가 아닙니다.</p>
    <textarea aria-label="나솔 원고 입력 JSON" className="w-full h-72 p-3 bg-card border border-border rounded font-mono text-sm" value={raw} onChange={e => setRaw(e.target.value)} />
    <button disabled={busy} onClick={generate} className="px-4 py-2 rounded bg-accent text-black disabled:opacity-50">{busy ? '생성 중...' : '검수용 원고 생성'}</button>
    {error && <p role="alert" className="text-red-400">{error}</p>}
    {media.media_error && <p role="alert" className="text-yellow-400">미디어 생성 안내: {media.media_error}</p>}
    {media.cards.length > 0 && <section className="space-y-3"><h2 className="font-semibold">검수용 카드뉴스 5장 (1:1)</h2><div className="grid grid-cols-2 md:grid-cols-3 gap-3">{media.cards.map((url, index) => <a key={url} href={url} download><img src={url} alt={`카드뉴스 ${index + 1}`} className="w-full rounded border border-border" /><span className="text-xs">카드 {index + 1} 저장</span></a>)}</div></section>}
    {media.video && <section className="space-y-2"><h2 className="font-semibold">세로 쇼츠 MP4 (무음 · 검수용)</h2><video controls className="max-w-xs w-full" src={media.video} /><a href={media.video} download className="underline block">MP4 저장</a></section>}
    {draft && <section className="space-y-3"><h2 className="font-semibold">{title}</h2><p className="text-sm text-yellow-400">미검증 초안 · 자동 발행되지 않음 · 이미지 사용권 별도 확인</p><pre className="whitespace-pre-wrap bg-card border border-border rounded p-4 text-sm">{draft}</pre></section>}
  </div>
}
