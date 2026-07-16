import { ImageResponse } from "next/og";

export const size = {
  width: 512,
  height: 512,
};

export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    <div
      style={{
        alignItems: "center",
        background: "#0b5d59",
        display: "flex",
        height: "100%",
        justifyContent: "center",
        width: "100%",
      }}
    >
      <div
        style={{
          alignItems: "center",
          background: "#eaf7f5",
          borderRadius: "28%",
          color: "#0b5d59",
          display: "flex",
          fontFamily: "Arial, sans-serif",
          fontSize: 260,
          fontWeight: 800,
          height: 360,
          justifyContent: "center",
          letterSpacing: -24,
          paddingRight: 24,
          width: 360,
        }}
      >
        P
      </div>
    </div>,
    size,
  );
}
