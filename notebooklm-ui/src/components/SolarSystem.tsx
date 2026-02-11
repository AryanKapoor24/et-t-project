import { useEffect, useRef } from "react";
import * as THREE from "three";
// Import OrbitControls and other addons from three/examples/jsm
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass";

export default function SolarSystem() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020205);
    scene.fog = new THREE.FogExp2(0x020205, 0.0005);

    // Camera
    const camera = new THREE.PerspectiveCamera(
      45,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      10000
    );
    camera.position.set(0, 80, 200);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 0.8;
    containerRef.current.appendChild(renderer.domElement);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 10;
    controls.maxDistance = 1000;

    // Starfield
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 8000;
    const starPositions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      const i3 = i * 3;
      const radius = 500 + Math.random() * 1500;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      starPositions[i3] = radius * Math.sin(phi) * Math.cos(theta);
      starPositions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      starPositions[i3 + 2] = radius * Math.cos(phi);
    }
    starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
    const starMaterial = new THREE.PointsMaterial({ color: 0xffffff, size: 0.8 });
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // Sun
    const sunGeometry = new THREE.SphereGeometry(10, 64, 64);
    const sunMaterial = new THREE.MeshBasicMaterial({ color: 0xffcc00 });
    const sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.position.set(0, 0, 0);
    scene.add(sun);

    // Planets
    const planetConfigs = [
      { name: 'Mercury', radius: 1, color: 0x8c8c8c, orbitRadius: 25, orbitSpeed: 4.1 },
      { name: 'Venus', radius: 2.4, color: 0xe6e6b8, orbitRadius: 35, orbitSpeed: 1.6 },
      { name: 'Earth', radius: 2.5, color: 0x2266ff, orbitRadius: 45, orbitSpeed: 1 },
      { name: 'Mars', radius: 1.3, color: 0xc1440e, orbitRadius: 55, orbitSpeed: 0.53 },
      { name: 'Jupiter', radius: 7, color: 0xd4a574, orbitRadius: 85, orbitSpeed: 0.084 },
      { name: 'Saturn', radius: 6, color: 0xe3dccb, orbitRadius: 120, orbitSpeed: 0.034 },
      { name: 'Uranus', radius: 4, color: 0xb8d4e3, orbitRadius: 160, orbitSpeed: 0.012 },
      { name: 'Neptune', radius: 3.9, color: 0x5b7cff, orbitRadius: 190, orbitSpeed: 0.006 }
    ];
    const planets = [];
    planetConfigs.forEach(config => {
      const geometry = new THREE.SphereGeometry(config.radius, 64, 64);
      let material;
      // Add basic textures for Earth
      if (config.name === 'Earth') {
        const earthTexture = new THREE.TextureLoader().load('https://upload.wikimedia.org/wikipedia/commons/9/97/The_Earth_seen_from_Apollo_17.jpg');
        material = new THREE.MeshStandardMaterial({ map: earthTexture, emissive: 0x2266ff, emissiveIntensity: 0.3 });
      } else {
        material = new THREE.MeshStandardMaterial({ color: config.color, emissive: config.color, emissiveIntensity: 0.3 });
      }
      const mesh = new THREE.Mesh(geometry, material);
      mesh.userData = { ...config };
      scene.add(mesh);
      planets.push(mesh);

      // Add orbit rings (yellow)
      const orbitRingGeometry = new THREE.RingGeometry(config.orbitRadius - 0.3, config.orbitRadius + 0.3, 128);
      const orbitRingMaterial = new THREE.MeshBasicMaterial({ color: 0xffff00, transparent: true, opacity: 0.5, side: THREE.DoubleSide });
      const orbitRing = new THREE.Mesh(orbitRingGeometry, orbitRingMaterial);
      orbitRing.rotation.x = Math.PI / 2;
      scene.add(orbitRing);

      // Add rings for Saturn
      if (config.name === 'Saturn') {
        const ringGeometry = new THREE.RingGeometry(config.radius * 1.2, config.radius * 2, 64);
        const ringMaterial = new THREE.MeshBasicMaterial({ color: 0xe3dccb, side: THREE.DoubleSide, transparent: true, opacity: 0.7 });
        const ring = new THREE.Mesh(ringGeometry, ringMaterial);
        ring.rotation.x = Math.PI / 2;
        ring.position.set(0, 0, 0);
        mesh.add(ring);
      }
    });

    // Add a moon orbiting Earth
    const moonGeometry = new THREE.SphereGeometry(0.7, 32, 32);
    const moonMaterial = new THREE.MeshStandardMaterial({ color: 0x888888 });
    const moon = new THREE.Mesh(moonGeometry, moonMaterial);
    scene.add(moon);

    // Animation loop
    const clock = new THREE.Clock();
    function animate() {
      requestAnimationFrame(animate);
      const time = clock.getElapsedTime();
      planets.forEach(planet => {
        const { orbitRadius, orbitSpeed, name } = planet.userData;
        const angle = time * orbitSpeed * 0.05;
        planet.position.x = Math.cos(angle) * orbitRadius;
        planet.position.z = Math.sin(angle) * orbitRadius;
        planet.rotation.y += 0.005;

        // Animate moon around Earth
        if (name === 'Earth') {
          const moonAngle = time * 0.5;
          moon.position.x = planet.position.x + Math.cos(moonAngle) * 6;
          moon.position.z = planet.position.z + Math.sin(moonAngle) * 6;
          moon.position.y = planet.position.y;
          moon.rotation.y += 0.01;
        }
      });
      sun.rotation.y += 0.001;
      stars.rotation.y += 0.00005;
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // Handle resize
    const handleResize = () => {
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    };
    window.addEventListener("resize", handleResize);

    // Clean up
    return () => {
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      if (containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ width: "100vw", height: "100vh", margin: 0, overflow: "hidden", background: "#000" }}
    />
  );
}
