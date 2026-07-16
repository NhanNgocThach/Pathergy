import { ImageResponse } from "next/og";

export const size = {
  width: 180,
  height: 180,
};

export const contentType = "image/png";

export default function AppleIcon() {
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
          fontSize: 92,
          fontWeight: 800,
          height: 126,
          justifyContent: "center",
          letterSpacing: -8,
          paddingRight: 8,
          width: 126,
        }}
      >
        P
      </div>
    </div>,
    size,
  );
}
