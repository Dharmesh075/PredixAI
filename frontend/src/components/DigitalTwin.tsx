import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { Machine } from '../types';
import { Activity, Gauge, Flame, AlertCircle, RotateCcw, Eye } from 'lucide-react';

interface DigitalTwinProps {
  machine?: Machine;
}

export const DigitalTwin: React.FC<DigitalTwinProps> = ({ machine }) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [wireframe, setWireframe] = useState(false);
  const [rotationSpeed, setRotationSpeed] = useState(1.0);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const fanBladesRef = useRef<THREE.Group | null>(null);
  const coreRef = useRef<THREE.Mesh | null>(null);

  const health = machine ? machine.health_score : 85;
  const isCritical = health < 40;
  const isWarning = health >= 40 && health < 80;

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight || 500;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    sceneRef.current = scene;
    scene.background = new THREE.Color(0x0a0f1d);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 5, 18);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    mountRef.current.appendChild(renderer.domElement);

    // 2. Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 1.2);
    dirLight1.position.set(10, 15, 10);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(isCritical ? 0xef4444 : (isWarning ? 0xf59e0b : 0x10b981), 1.5);
    dirLight2.position.set(-10, -5, -10);
    scene.add(dirLight2);

    // 3. Turbofan Model Construction
    const engineGroup = new THREE.Group();
    scene.add(engineGroup);

    // A. Outer Nacelle (Cowl)
    const nacelleGeo = new THREE.CylinderGeometry(4.2, 4.0, 12, 32, 1, true);
    const nacelleMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      metalness: 0.8,
      roughness: 0.3,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.45,
      wireframe: wireframe
    });
    const nacelle = new THREE.Mesh(nacelleGeo, nacelleMat);
    nacelle.rotation.x = Math.PI / 2;
    engineGroup.add(nacelle);

    // B. Nacelle Rings (Inlet & Exhaust Lips)
    const lipGeo = new THREE.TorusGeometry(4.2, 0.25, 16, 64);
    const lipMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.9, roughness: 0.2 });
    const inletLip = new THREE.Mesh(lipGeo, lipMat);
    inletLip.position.z = 6;
    engineGroup.add(inletLip);

    const exhaustLip = new THREE.Mesh(lipGeo, lipMat);
    exhaustLip.position.z = -6;
    engineGroup.add(exhaustLip);

    // C. Center Shaft & Spinner Nose Cone
    const spinnerGeo = new THREE.ConeGeometry(1.4, 3.5, 32);
    const spinnerMat = new THREE.MeshStandardMaterial({ color: 0x0ea5e9, metalness: 0.9, roughness: 0.1 });
    const spinner = new THREE.Mesh(spinnerGeo, spinnerMat);
    spinner.rotation.x = Math.PI / 2;
    spinner.position.z = 5.2;

    const fanGroup = new THREE.Group();
    fanGroup.add(spinner);

    // D. Rotating Fan Blades (18 titanium wide-chord blades)
    const bladeGeo = new THREE.BoxGeometry(0.12, 2.8, 0.6);
    const bladeMat = new THREE.MeshStandardMaterial({
      color: 0x94a3b8,
      metalness: 0.85,
      roughness: 0.2
    });

    const numBlades = 18;
    for (let i = 0; i < numBlades; i++) {
      const angle = (i / numBlades) * Math.PI * 2;
      const blade = new THREE.Mesh(bladeGeo, bladeMat);
      blade.position.set(Math.cos(angle) * 2.2, Math.sin(angle) * 2.2, 4.2);
      blade.rotation.z = angle;
      blade.rotation.x = 0.35; // Aerodynamic pitch angle
      fanGroup.add(blade);
    }
    engineGroup.add(fanGroup);
    fanBladesRef.current = fanGroup;

    // E. High Pressure Compressor (HPC) & Combustion Core (Color-coded by thermal wear)
    const coreColor = isCritical ? 0xef4444 : (isWarning ? 0xf59e0b : 0x0284c7);
    const coreGeo = new THREE.CylinderGeometry(2.0, 1.6, 7.5, 24);
    const coreMat = new THREE.MeshStandardMaterial({
      color: coreColor,
      metalness: 0.6,
      roughness: 0.4,
      emissive: coreColor,
      emissiveIntensity: isCritical ? 0.7 : 0.2
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    core.rotation.x = Math.PI / 2;
    core.position.z = -0.5;
    engineGroup.add(core);
    coreRef.current = core;

    // F. Compressor Stage Stator Disks
    for (let d = -3; d <= 2; d += 1.2) {
      const diskGeo = new THREE.TorusGeometry(2.1, 0.08, 12, 32);
      const diskMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
      const disk = new THREE.Mesh(diskGeo, diskMat);
      disk.position.z = d;
      engineGroup.add(disk);
    }

    // Grid Floor
    const grid = new THREE.GridHelper(30, 30, 0x1e293b, 0x0f172a);
    grid.position.y = -6;
    scene.add(grid);

    // Mouse Drag Rotation
    let isDragging = false;
    let prevMouseX = 0;
    let prevMouseY = 0;

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaX = e.clientX - prevMouseX;
      const deltaY = e.clientY - prevMouseY;
      engineGroup.rotation.y += deltaX * 0.008;
      engineGroup.rotation.x += deltaY * 0.008;
      prevMouseX = e.clientX;
      prevMouseY = e.clientY;
    };

    const onMouseUp = () => { isDragging = false; };

    const dom = renderer.domElement;
    dom.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);

    // 4. Animation Loop
    let animId: number;
    const animate = () => {
      animId = requestAnimationFrame(animate);

      // Rotate fan blades
      if (fanBladesRef.current) {
        fanBladesRef.current.rotation.z += 0.08 * rotationSpeed;
      }

      // Gentle auto-sway when not dragging
      if (!isDragging) {
        engineGroup.rotation.y += 0.002;
      }

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight || 500;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animId);
      dom.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      window.removeEventListener('resize', handleResize);
      if (mountRef.current) {
        mountRef.current.innerHTML = '';
      }
      renderer.dispose();
    };
  }, [wireframe, rotationSpeed, isCritical, isWarning]);

  return (
    <div className="relative w-full h-[620px] rounded-2xl bg-gradient-to-b from-[#0F172A] to-[#0B0F17] border border-slate-800 overflow-hidden shadow-2xl flex flex-col">
      {/* Top Overlay Header */}
      <div className="absolute top-4 left-6 right-6 flex items-center justify-between z-10 pointer-events-none">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
            <h3 className="font-extrabold text-white text-lg tracking-tight">
              3D Digital Twin Simulation
            </h3>
            <span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-400 font-mono text-xs border border-sky-500/30">
              {machine?.machine_id || 'ENG-001'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Full-fidelity turbofan aerothermal & structural degradation model
          </p>
        </div>

        {/* Live Status Pill */}
        <div className="pointer-events-auto flex items-center gap-3">
          <div className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center gap-2 ${
            isCritical
              ? 'bg-red-500/20 border-red-500/40 text-red-400'
              : (isWarning ? 'bg-amber-500/20 border-amber-500/40 text-amber-400' : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400')
          }`}>
            <Flame className="w-3.5 h-3.5" />
            <span>Core State: {isCritical ? 'Thermal Wear Limit' : (isWarning ? 'Moderate Degradation' : 'Nominal Aerodynamics')}</span>
          </div>
        </div>
      </div>

      {/* 3D WebGL Canvas */}
      <div ref={mountRef} className="w-full flex-1 cursor-grab active:cursor-grabbing" />

      {/* Bottom Controls & Telemetry HUD */}
      <div className="h-20 bg-slate-900/90 backdrop-blur border-t border-slate-800 px-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-6 text-xs font-mono">
          <div>
            <span className="text-slate-400 block text-[10px]">FAN RPM (Nf)</span>
            <span className="text-white font-bold text-sm">2,388 RPM</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">CORE TEMP (T30)</span>
            <span className={`font-bold text-sm ${isCritical ? 'text-red-400' : 'text-emerald-400'}`}>
              1,589.7 °R
            </span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">HPC PRESSURE (Ps30)</span>
            <span className="text-cyan-400 font-bold text-sm">47.5 psia</span>
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">RUL PROGNOSIS</span>
            <span className="text-amber-400 font-bold text-sm">{machine?.predicted_rul.toFixed(1) || '122.2'} Cycles</span>
          </div>
        </div>

        {/* Interactive View Controls */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setWireframe(!wireframe)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors flex items-center gap-1.5 ${
              wireframe ? 'bg-sky-500/20 border-sky-500 text-sky-400' : 'bg-slate-800 border-slate-700 text-slate-300'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Wireframe Cowl</span>
          </button>

          <button
            onClick={() => setRotationSpeed(rotationSpeed === 1.0 ? 2.5 : 1.0)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 border border-slate-700 text-slate-300 hover:text-white transition-colors flex items-center gap-1.5"
          >
            <Gauge className="w-3.5 h-3.5 text-cyan-400" />
            <span>Throttle: {rotationSpeed === 1.0 ? '100%' : '150%'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
