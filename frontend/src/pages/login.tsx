import { useEffect, useState } from "react";

export default function Login() {
  const [a, setA] = useState("a");

  useEffect(() => {
    if (a) {
      console.log("a");
    }
  }, []);

  return <div>login</div>;
}
