import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const NAVY = '#070b14';
const BLUE = '#00529B';
const GOLD = '#FECB00';
const ICE = '#E8EEF7';

const WORDS = [
  {sv: 'Hej', th: 'สวัสดี', img: 'hej.png'},
  {sv: 'Tack', th: 'ขอบคุณ', img: 'tack.png'},
  {sv: 'Fika', th: 'พักกาแฟ', img: 'fika.png'},
  {sv: 'Äpple', th: 'แอปเปิ้ล', img: 'apple.png'},
];

const FEATURES = [
  {emoji: '📘', title: '25 บทเรียน', sub: 'Beginner → Intermediate'},
  {emoji: '⌨️', title: 'ฝึกพิมพ์', sub: 'โจทย์ภาษาไทย → สวีเดน'},
  {emoji: '🎯', title: 'เกมจับคู่', sub: 'ภาพใหญ่ + คำแปล'},
  {emoji: '🤖', title: 'ครู AI', sub: 'อธิบายเป็นภาษาไทย'},
];

const pop = (frame: number, fps: number, delay: number, from = 0.7) =>
  spring({frame: frame - delay, fps, config: {damping: 14, mass: 0.7, stiffness: 140}});

const SceneAudio: React.FC<{file: string; volume?: number}> = ({file, volume = 0.55}) => {
  return <Audio src={staticFile(file)} volume={volume} />;
};

const FlagGlow: React.FC = () => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 720], [0, 80]);
  return (
    <AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: `radial-gradient(900px 480px at ${18 + drift / 8}% -10%, rgba(0,82,155,0.5), transparent 55%),
            radial-gradient(700px 420px at 110% 10%, rgba(254,203,0,0.16), transparent 50%),
            ${NAVY}`,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 86,
          height: 18,
          width: '100%',
          background: BLUE,
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 92,
          height: 6,
          width: '100%',
          background: GOLD,
        }}
      />
    </AbsoluteFill>
  );
};

const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = pop(frame, fps, 4);
  const fade = interpolate(frame, [0, 12, 50, 70], [0, 1, 1, 0], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: fade}}>
      <div
        style={{
          transform: `scale(${0.8 + s * 0.2})`,
          textAlign: 'center',
          fontFamily: 'Outfit, Kanit, sans-serif',
        }}
      >
        <div style={{fontSize: 92}}>🇸🇪</div>
        <div style={{fontSize: 160, fontWeight: 800, color: GOLD, letterSpacing: -4}}>Hej!</div>
        <div style={{marginTop: 8, fontSize: 36, color: ICE, opacity: 0.8}}>เรียนภาษาสวีเดนสำหรับคนไทย</div>
      </div>
    </AbsoluteFill>
  );
};

const Title: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = pop(frame, fps, 2);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{transform: `translateY(${(1 - s) * 40}px)`, opacity: s, textAlign: 'center'}}>
        <div style={{fontSize: 28, letterSpacing: 10, color: GOLD, fontWeight: 700}}>SVENSKAEASY</div>
        <div
          style={{
            marginTop: 12,
            fontSize: 92,
            fontWeight: 800,
            color: 'white',
            fontFamily: 'Outfit, Kanit, sans-serif',
          }}
        >
          SvenskaEasy
        </div>
        <div style={{marginTop: 16, fontSize: 34, color: ICE, opacity: 0.75}}>
          เรียนสวีเดน ให้รู้เรื่องจริง
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Features: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{width: 1500}}>
        <div style={{fontSize: 42, color: GOLD, fontWeight: 800, marginBottom: 36}}>ฟีเจอร์เด่น</div>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 28}}>
          {FEATURES.map((item, i) => {
            const s = pop(frame, fps, 6 + i * 7);
            return (
              <div
                key={item.title}
                style={{
                  transform: `translateY(${(1 - s) * 50}px) scale(${0.92 + s * 0.08})`,
                  opacity: s,
                  background: 'linear-gradient(135deg, rgba(0,82,155,0.35), rgba(16,24,39,0.9))',
                  border: '1px solid rgba(254,203,0,0.25)',
                  borderRadius: 28,
                  padding: '32px 36px',
                  display: 'flex',
                  gap: 22,
                  alignItems: 'center',
                }}
              >
                <div style={{fontSize: 64}}>{item.emoji}</div>
                <div>
                  <div style={{fontSize: 36, fontWeight: 800, color: 'white'}}>{item.title}</div>
                  <div style={{fontSize: 22, color: ICE, opacity: 0.7, marginTop: 6}}>{item.sub}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const WordFlash: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{textAlign: 'center'}}>
        <div style={{fontSize: 28, color: GOLD, letterSpacing: 6, fontWeight: 700, marginBottom: 28}}>
          คลังคำศัพท์ + รูปภาพ
        </div>
        <div style={{display: 'flex', gap: 28}}>
          {WORDS.map((w, i) => {
            const s = pop(frame, fps, 4 + i * 8);
            return (
              <div
                key={w.sv}
                style={{
                  width: 280,
                  transform: `translateY(${(1 - s) * 60}px)`,
                  opacity: s,
                  background: '#101827',
                  borderRadius: 28,
                  overflow: 'hidden',
                  border: '2px solid rgba(254,203,0,0.3)',
                }}
              >
                <Img src={staticFile(w.img)} style={{width: '100%', height: 180, objectFit: 'cover'}} />
                <div style={{padding: 18}}>
                  <div style={{fontSize: 40, fontWeight: 800, color: GOLD}}>{w.sv}</div>
                  <div style={{fontSize: 20, color: ICE, opacity: 0.75}}>{w.th}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Stack: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const items = ['FastAPI', 'Tailwind', 'MongoDB', 'ครู AI', 'Admin Console'];
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{textAlign: 'center'}}>
        <div style={{fontSize: 52, fontWeight: 800, color: 'white', marginBottom: 40}}>
          สแต็กที่พร้อมใช้งานจริง
        </div>
        <div style={{display: 'flex', gap: 18, justifyContent: 'center'}}>
          {items.map((label, i) => {
            const s = pop(frame, fps, 5 + i * 6);
            return (
              <div
                key={label}
                style={{
                  transform: `scale(${s})`,
                  opacity: s,
                  padding: '18px 28px',
                  borderRadius: 999,
                  background: i % 2 === 0 ? BLUE : GOLD,
                  color: i % 2 === 0 ? 'white' : '#002B5C',
                  fontSize: 26,
                  fontWeight: 800,
                }}
              >
                {label}
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = pop(frame, fps, 2);
  const glow = interpolate(frame, [0, 30, 60], [0.2, 0.55, 0.2], {extrapolateRight: 'extend'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{transform: `scale(${0.86 + s * 0.14})`, opacity: s, textAlign: 'center'}}>
        <div style={{fontSize: 34, color: GOLD, letterSpacing: 8, fontWeight: 700}}>START LEARNING</div>
        <div style={{fontSize: 84, fontWeight: 800, color: 'white', marginTop: 10}}>localhost:8000</div>
        <div
          style={{
            margin: '28px auto 0',
            width: 420,
            padding: '16px 0',
            borderRadius: 18,
            background: GOLD,
            color: '#002B5C',
            fontSize: 28,
            fontWeight: 800,
            boxShadow: `0 0 ${40 + glow * 40}px rgba(254,203,0,0.45)`,
          }}
        >
          เปิด SvenskaEasy
        </div>
        <div style={{marginTop: 22, fontSize: 22, color: ICE, opacity: 0.7}}>Hej då — แล้วมาเรียนกัน</div>
      </div>
    </AbsoluteFill>
  );
};

export const LearnSwedishPromo: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: NAVY,
        fontFamily: 'Kanit, Outfit, sans-serif',
        color: ICE,
      }}
    >
      <FlagGlow />
      <Audio src={staticFile('music.wav')} volume={0.38} />

      <Sequence from={0} durationInFrames={75}>
        <Intro />
        <SceneAudio file="whoosh.wav" volume={0.5} />
      </Sequence>
      <Sequence from={70} durationInFrames={100}>
        <Title />
        <SceneAudio file="ding.wav" volume={0.45} />
      </Sequence>
      <Sequence from={165} durationInFrames={145}>
        <Features />
        <SceneAudio file="pop.wav" volume={0.5} />
      </Sequence>
      <Sequence from={305} durationInFrames={155}>
        <WordFlash />
        <SceneAudio file="whoosh.wav" volume={0.42} />
      </Sequence>
      <Sequence from={455} durationInFrames={120}>
        <Stack />
        <SceneAudio file="click.wav" volume={0.55} />
      </Sequence>
      <Sequence from={565} durationInFrames={155}>
        <Outro />
        <SceneAudio file="ding.wav" volume={0.5} />
      </Sequence>
    </AbsoluteFill>
  );
};
