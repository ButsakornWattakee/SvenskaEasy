import React from 'react';
import {Composition} from 'remotion';
import {LearnSwedishPromo} from './LearnSwedishPromo';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SvenskaEasyPromo"
        component={LearnSwedishPromo}
        durationInFrames={720}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
