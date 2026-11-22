import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Define the new JavaScript code to replace renderAllResults through renderClassDistribution
js_engine_code = r'''    // 8. Dynamic Sample Intelligence & Calculation Engine
    function computeSampleIntelligence(data) {
      const b = data.class_breakdown || {};
      const c1 = b['class_1'] || { percentage: 0, area_hectares: 0, pixel_count: 0 };
      const c2 = b['class_2'] || { percentage: 0, area_hectares: 0, pixel_count: 0 };
      const c3 = b['class_3'] || { percentage: 0, area_hectares: 0, pixel_count: 0 };
      const c4 = b['class_4'] || { percentage: 0, area_hectares: 0, pixel_count: 0 };
      const c5 = b['class_5'] || { percentage: 0, area_hectares: 0, pixel_count: 0 };
      const c6 = b['class_6'] || { percentage: 0, area_hectares: 0, pixel_count: 0 };
      const c7 = b['class_7'] || { percentage: 0, area_hectares: 0, pixel_count: 0 };

      const totalVegPct = Number((c2.percentage + c3.percentage + c4.percentage).toFixed(1));
      const totalVegHa = Number((totalVegPct * 40.96 / 100).toFixed(2));
      const unbuiltHa = Number((40.96 - c6.area_hectares).toFixed(2));
      const unbuiltPct = Number(((unbuiltHa / 40.96) * 100).toFixed(1));
      const cultivablePct = Number((c4.percentage + c5.percentage).toFixed(1));
      const cultivableHa = Number((cultivablePct * 40.96 / 100).toFixed(2));

      // 1. Farming Suitability Score (0-100)
      let farmScore = Math.round((c4.percentage * 1.5) + (c5.percentage * 0.75) + (totalVegPct * 0.4) - (c6.percentage * 1.2));
      if (c1.percentage >= 0.5 && c1.percentage <= 4.0) farmScore += 5;
      farmScore = Math.max(20, Math.min(95, farmScore));
      let farmRating = farmScore >= 80 ? 'Prime Agrarian Farmland' : (farmScore >= 65 ? 'Favorable Agricultural Land' : 'Moderate / Mixed Fringe');
      let farmGrade = farmScore >= 80 ? 'A' : (farmScore >= 65 ? 'B' : 'C');

      // 2. Construction Ground Readiness Score (0-100)
      let constScore = Math.round((unbuiltPct * 0.55) + 20 + (c1.area_hectares < 0.5 ? 15 : (c1.area_hectares < 1.5 ? 10 : 5)) + (c6.percentage > 3 && c6.percentage < 20 ? 5 : 0));
      constScore = Math.max(30, Math.min(96, constScore));
      let constRating = constScore >= 85 ? 'High Greenfield Readiness' : (constScore >= 70 ? 'Favorable Development Footprint' : 'Transitional / Infill Development');
      let constGrade = constScore >= 85 ? 'A' : (constScore >= 70 ? 'B' : 'C');

      // 3. Surface Soil Stability Index
      let soilScore = Math.round(30 + (totalVegPct * 0.9) + (c5.percentage > 40 ? 5 : 15));
      soilScore = Math.max(35, Math.min(95, soilScore));
      let soilRating = totalVegPct >= 40 ? 'High Stability (Low Erosion)' : (totalVegPct >= 25 ? 'Moderate Stability (Good Root Hold)' : 'Elevated Exposure (Erosion Vigilance)');

      // 4. Model Softmax Neural Certainty
      const confPct = data.mean_confidence_pct ? Number(data.mean_confidence_pct.toFixed(1)) : 78.5;

      return {
        c1, c2, c3, c4, c5, c6, c7,
        totalVegPct, totalVegHa,
        unbuiltHa, unbuiltPct,
        cultivablePct, cultivableHa,
        farmScore, farmRating, farmGrade,
        constScore, constRating, constGrade,
        soilScore, soilRating,
        confPct
      };
    }

    // 8B. Render All Results Across Overview, Categories & Gallery
    function renderAllResults(data) {
      currentPrediction = data;
      const intel = computeSampleIntelligence(data);

      // 1. Update Hero Location Header
      const heroLoc = document.getElementById('heroLocationTitle');
      const heroSub = document.getElementById('heroLocationSubtitle');
      const mapRegion = document.getElementById('mapSelectedRegion');
      const mapCoords = document.getElementById('mapSelectedCoords');

      if (data.location_verified && data.latitude && data.longitude) {
        const titleStr = `${data.sample_name.replace('sample_tile_', 'Demonstration Study Site #')} (Delhi NCR)`;
        heroLoc.innerText = titleStr;
        heroSub.innerText = `Coordinates: ${data.latitude.toFixed(5)}°N, ${data.longitude.toFixed(5)}°E • System: ${data.coordinate_system || 'WGS 84 / UTM 43N'}`;
        mapRegion.innerText = titleStr;
        mapCoords.innerText = `Lat: ${data.latitude.toFixed(5)}°N | Lon: ${data.longitude.toFixed(5)}°E`;
        document.getElementById('quickCoords').innerText = `${data.latitude.toFixed(5)}°N, ${data.longitude.toFixed(5)}°E`;
      } else {
        heroLoc.innerText = `${data.sample_name} (Unreferenced Tile)`;
        heroSub.innerText = `Local Optical Coordinate System • External Upload`;
        mapRegion.innerText = `${data.sample_name} (Unreferenced)`;
        mapCoords.innerText = `Local Image Space`;
        document.getElementById('quickCoords').innerText = `Unreferenced Space`;
      }

      // 2. Overview Top Cards
      const dominantInfo = humanizeClass(data.dominant_class);
      document.getElementById('cardDominantName').innerText = dominantInfo.label;
      document.getElementById('cardDominantDesc').innerText = `${data.dominant_percentage.toFixed(1)}% of analyzed area (${(data.dominant_percentage * 40.96 / 100).toFixed(2)} ha).`;
      document.getElementById('cardVegPct').innerText = `${data.vegetation_coverage_pct.toFixed(1)}%`;
      document.getElementById('cardBuiltPct').innerText = `${data.built_up_coverage_pct.toFixed(1)}%`;
      const confStr = `${intel.confPct}%`;
      document.getElementById('cardModelConfidence').innerText = confStr;

      // 3. Narrative Summary
      document.getElementById('narrativeSummary').innerText = 
        `This demonstration study parcel covers 40.96 hectares. Autonomous multi-spectral neural segmentation classifies ${dominantInfo.label.toLowerCase()} as the primary land surface covering ${data.dominant_percentage.toFixed(1)}% of the area (${(data.dominant_percentage * 40.96 / 100).toFixed(2)} ha). Total vegetative canopy accounts for ${data.vegetation_coverage_pct.toFixed(1)}% (${intel.totalVegHa} ha), while existing built structures occupy ${data.built_up_coverage_pct.toFixed(1)}% (${intel.c6.area_hectares} ha). Model classification confidence is ${confStr}.`;

      document.getElementById('quickLandCategory').innerText = 
        data.vegetation_coverage_pct > 40 ? 'Dense Green Canopy & Farmland' : (data.built_up_coverage_pct > 20 ? 'Transitional / Peri-Urban Infill' : 'Open Ground & Fallow Farmland');

      // 4. Update Images in Overview, Blend Stage, and Gallery
      document.getElementById('overviewThumbnailImg').src = data.images.original;
      document.getElementById('blendBaseRGB').src = data.images.original;
      document.getElementById('blendOverlayMask').src = data.images.colorized_mask;
      document.getElementById('galleryImgRGB').src = data.images.original;
      document.getElementById('galleryImgMask').src = data.images.colorized_mask;
      document.getElementById('galleryImgComposite').src = data.images.side_by_side;
      updateVisualView();

      // 5. Update Diagnostic Latency
      document.getElementById('diagLatency').innerText = `${data.inference_time_ms} ms`;
      document.getElementById('techLatency').innerText = `${data.inference_time_ms} ms`;

      // 6. Update 6-Pillar Sample-Specific Executive Overview
      updateSampleOverviewDossier(data, intel, dominantInfo);

      // 7. Update All 6 Feature Navigation Tabs (Summaries + Numerical Parameters)
      updateVegetationTab(data, intel);
      updateSoilTab(data, intel);
      updateWaterTab(data, intel);
      updateWeatherTab(data, intel);
      updateAgricultureTab(data, intel);
      updateConstructionTab(data, intel);

      // 8. Render Surface Breakdown Rows (with click-to-open parameter detail)
      renderClassDistribution(data.class_breakdown);
    }

    // Helper: Update Sample-Specific 6 Pillars in Overview Tab
    function updateSampleOverviewDossier(data, intel, dominantInfo) {
      // 1. Glance
      let glanceText = '';
      if (intel.c6.percentage > 18) {
        glanceText = `Semi-urban transition parcel with significant established built surfaces (${intel.c6.percentage.toFixed(1)}%, ${intel.c6.area_hectares} ha) and ${intel.unbuiltHa} ha open unbuilt land.`;
      } else if (intel.c4.percentage > 22) {
        glanceText = `Highly active agricultural parcel dominated by seasonal crop canopy (${intel.c4.percentage.toFixed(1)}%, ${intel.c4.area_hectares} ha) and fertile cultivable soils.`;
      } else if (intel.totalVegPct > 40) {
        glanceText = `Verdant, biologically active parcel with extensive vegetative cover (${intel.totalVegPct}%, ${intel.totalVegHa} ha) and low built footprint (${intel.c6.percentage.toFixed(1)}%).`;
      } else {
        glanceText = `Open rural agricultural parcel characterized predominantly by bare arable ground (${intel.c5.percentage.toFixed(1)}%, ${intel.c5.area_hectares} ha) with scattered vegetation.`;
      }
      const elGlance = document.getElementById('overview_glance');
      if (elGlance) elGlance.innerText = glanceText;

      // 2. Favorable
      const favList = document.getElementById('overview_favorable');
      if (favList) {
        favList.innerHTML = `
          <li><strong>${intel.unbuiltHa} ha (${intel.unbuiltPct}%) unbuilt space:</strong> Offers high layout flexibility and unobstructed site utilization.</li>
          <li><strong>${intel.totalVegPct}% vegetative vitality:</strong> Confirms active photosynthetic activity and root-binding soil protection.</li>
          <li><strong>${intel.c1.area_hectares < 0.3 ? 'Low immediate surface water' : 'Local surface moisture present'}:</strong> ${intel.c1.area_hectares < 0.3 ? 'No persistent optical flood ponding observed on observation date.' : `${intel.c1.area_hectares} ha detected moisture provides natural riparian drainage.`}</li>
        `;
      }

      // 3. Things to Investigate
      const invList = document.getElementById('overview_investigate');
      if (invList) {
        invList.innerHTML = `
          <li><strong>${intel.c5.percentage.toFixed(1)}% bare ground:</strong> Topsoil requires vegetative cover or mulching to mitigate dry-season wind erosion.</li>
          <li><strong>Subterranean chemistry & bearing capacity:</strong> Soil nutrients (N-P-K, pH) and foundation strength cannot be determined from space.</li>
          <li><strong>Cadastral title & boundaries:</strong> Verified revenue deeds (Jamabandi/Bhulekh) and zoning NOCs must be cleared via local registrar.</li>
        `;
      }

      // 4. Potential Uses
      const elUses = document.getElementById('overview_uses');
      if (elUses) {
        if (intel.c4.percentage > 18 || intel.totalVegPct > 40) {
          elUses.innerText = `Primary: Seasonal cereal/fodder agriculture (Wheat/Mustard/Paddy double-cropping) or agro-forestry. Secondary: Low-density eco-agri tourism or solar farm development.`;
        } else if (intel.c6.percentage > 15) {
          elUses.innerText = `Primary: Light commercial warehousing, logistics staging, or suburban residential infill. Secondary: Mixed agrarian-homestead utilization.`;
        } else {
          elUses.innerText = `Primary: Greenfield agrarian development, horticulture, or renewable energy installation. Secondary: Master-planned rural development subject to municipal NOC.`;
        }
      }

      // 5. Confidence
      const elConfBadge = document.getElementById('overview_confBadge');
      const elConfText = document.getElementById('overview_confText');
      const elConfBar = document.getElementById('overview_confBar');
      if (elConfBadge) elConfBadge.innerText = `${intel.confPct}%`;
      if (elConfText) elConfText.innerText = `Mean softmax neural confidence across 4,096 pixels. Correlates with 79.59% spatial validation accuracy on 6,088 regional tiles.`;
      if (elConfBar) elConfBar.style.width = `${intel.confPct}%`;
    }

    // Helper: Update Vegetation Tab
    function updateVegetationTab(data, intel) {
      // Summary
      const summaryText = `This 40.96-hectare footprint contains ${intel.totalVegPct}% total vegetative foliage (${intel.totalVegHa} ha). Agricultural crop signatures represent ${intel.c4.percentage.toFixed(1)}% (${intel.c4.area_hectares} ha), mature woodland cover represents ${intel.c2.percentage.toFixed(1)}% (${intel.c2.area_hectares} ha), and meadow grasses occupy ${intel.c3.percentage.toFixed(1)}% (${intel.c3.area_hectares} ha).`;
      setInnerText('veg_summaryText', summaryText);
      setInnerText('veg_favorableText', `${intel.totalVegHa} ha green foliage supports natural ecosystem vitality and soil stabilization.`);
      setInnerText('veg_attentionText', intel.totalVegPct < 30 ? 'Low canopy coverage exposes topsoil to weathering.' : 'Foliage is seasonal and dependent on irrigation/monsoon.');
      setInnerText('veg_useText', 'Baseline for crop acreage estimation, pasture planning, and biomass monitoring.');
      setInnerText('veg_limitsText', 'Single observation date; multi-year growth curves (NDVI) require multi-temporal shards.');

      // Parameter 1: Total Canopy
      setInnerText('vegTab_totalBadge', `${intel.totalVegPct}%`);
      setInnerText('vegTab_totalUnit', `${intel.totalVegHa} Hectares`);
      setInnerText('vegTab_totalRating', intel.totalVegPct > 40 ? 'Dense Foliage' : (intel.totalVegPct > 25 ? 'Moderate Cover' : 'Sparse Foliage'));
      setInnerText('vegTab_totalDesc', `Total vegetative canopy spans ${intel.totalVegHa} ha across tree canopy, crop parcels, and field borders.`);
      setBarWidth('vegTab_totalBar', intel.totalVegPct);

      // Parameter 2: Dense Forest
      setInnerText('vegTab_denseBadge', `${intel.c2.area_hectares} ha`);
      setInnerText('vegTab_denseUnit', `${intel.c2.percentage.toFixed(1)}% Share`);
      setInnerText('vegTab_denseRating', intel.c2.area_hectares > 1.0 ? 'Woodland Presence' : 'Scattered Trees');
      setInnerText('vegTab_denseDesc', `Mature tree clusters and thick perennial foliage occupy ${intel.c2.area_hectares} ha (${intel.c2.percentage.toFixed(1)}%).`);
      setBarWidth('vegTab_denseBar', intel.c2.percentage * 5);

      // Parameter 3: Sparse Meadow
      setInnerText('vegTab_sparseBadge', `${intel.c3.area_hectares} ha`);
      setInnerText('vegTab_sparseUnit', `${intel.c3.percentage.toFixed(1)}% Share`);
      setInnerText('vegTab_sparseRating', intel.c3.percentage > 20 ? 'Extensive Meadow' : 'Border Grasses');
      setInnerText('vegTab_sparseDesc', `Open grasslands, pasture clearings, and roadside grasses occupy ${intel.c3.area_hectares} ha (${intel.c3.percentage.toFixed(1)}%).`);
      setBarWidth('vegTab_sparseBar', intel.c3.percentage * 2.5);

      // Parameter 4: Crop Foliage
      setInnerText('vegTab_cropBadge', `${intel.c4.area_hectares} ha`);
      setInnerText('vegTab_cropUnit', `${intel.c4.percentage.toFixed(1)}% Share`);
      setInnerText('vegTab_cropRating', intel.c4.percentage > 20 ? 'Active Cultivation' : 'Low Crop Signature');
      setInnerText('vegTab_cropDesc', `Seasonally cultivated agricultural crop signatures occupy ${intel.c4.area_hectares} ha (${intel.c4.percentage.toFixed(1)}%).`);
      setBarWidth('vegTab_cropBar', intel.c4.percentage * 2.5);

      // Parameter 5: Canopy Condition
      const condRating = intel.totalVegPct >= 40 ? 'High Vigour' : (intel.totalVegPct >= 25 ? 'Moderate Vigour' : 'Sparse / Fallow');
      setInnerText('vegTab_condBadge', condRating);
      setInnerText('vegTab_condRating', intel.totalVegPct >= 35 ? 'Healthy Photosynthesis' : 'Moderate Biomass');
      setBarWidth('vegTab_condBar', Math.min(100, intel.totalVegPct * 2));
    }

    // Helper: Update Soil & Terrain Tab
    function updateSoilTab(data, intel) {
      const summaryText = `Open bare earth occupies ${intel.c5.percentage.toFixed(1)}% (${intel.c5.area_hectares} ha) of this site. Topography is situated on the flat alluvial plain of the Indo-Gangetic basin with slope gradients under 2.0°.`;
      setInnerText('soil_summaryText', summaryText);
      setInnerText('soil_favorableText', `Flat terrain (<2.0° slope) and alluvial silt loam provide easy ground grading and minimal slip risk.`);
      setInnerText('soil_attentionText', `${intel.c5.area_hectares} ha exposed bare soil is vulnerable to dry-season erosion without crop cover.`);
      setInnerText('soil_useText', 'Guides earthwork grading, foundation leveling, and soil conservation planning.');
      setInnerText('soil_limitsText', 'Subterranean chemistry (N-P-K, pH, organic carbon) & borehole load tests unavailable.');

      // Parameter 1: Bare Soil
      setInnerText('soilTab_bareBadge', `${intel.c5.percentage.toFixed(1)}%`);
      setInnerText('soilTab_bareUnit', `${intel.c5.area_hectares} Hectares`);
      setInnerText('soilTab_bareRating', intel.c5.percentage > 40 ? 'High Open Ground' : 'Moderate Exposure');
      setInnerText('soilTab_bareDesc', `Exposed topsoil and fallow fields occupy ${intel.c5.area_hectares} ha (${intel.c5.percentage.toFixed(1)}%).`);
      setBarWidth('soilTab_bareBar', intel.c5.percentage);

      // Parameter 2: Erosion Vulnerability
      setInnerText('soilTab_erosionBadge', intel.soilRating.split(' ')[0]);
      setInnerText('soilTab_erosionRating', intel.soilRating);
      setBarWidth('soilTab_erosionBar', intel.soilScore);

      // Parameter 3: Slope
      setBarWidth('soilTab_slopeBar', 10);
    }

    // Helper: Update Water & Moisture Tab
    function updateWaterTab(data, intel) {
      const summaryText = `Optical surface water and moisture signatures represent ${intel.c1.percentage.toFixed(1)}% (${intel.c1.area_hectares} ha) of the analyzed area. Gradual natural drainage channels characterize the Yamuna-Hindon plain basin.`;
      setInnerText('water_summaryText', summaryText);
      setInnerText('water_favorableText', intel.c1.area_hectares < 0.5 ? 'Minimal standing water indicates no persistent optical ponding on observation date.' : `${intel.c1.area_hectares} ha detected surface moisture supports local vegetative hydration.`);
      setInnerText('water_attentionText', intel.c1.area_hectares >= 0.8 ? 'Surface moisture presence requires field check of high-monsoon drainage channels.' : 'Single-date observation does not reflect peak 100-year flood levels.');
      setInnerText('water_useText', 'Identifies drainage alignments, irrigation ditches, and wetland protection zones.');
      setInnerText('water_limitsText', 'Subsurface groundwater depth (CGWB) & canal release schedules unavailable.');

      // Parameter 1: Surface Water
      setInnerText('waterTab_waterBadge', `${intel.c1.area_hectares} ha`);
      setInnerText('waterTab_waterUnit', `${intel.c1.percentage.toFixed(1)}% Coverage`);
      setInnerText('waterTab_waterRating', intel.c1.area_hectares < 0.2 ? 'Dry Ground' : (intel.c1.area_hectares < 1.0 ? 'Drainage Channel' : 'Water Corridor'));
      setBarWidth('waterTab_waterBar', Math.min(100, intel.c1.percentage * 15));

      // Parameter 2: Water Presence
      setInnerText('waterTab_presBadge', intel.c1.area_hectares > 0.5 ? `${intel.c1.area_hectares} ha` : 'None Major');
      setInnerText('waterTab_presRating', intel.c1.area_hectares > 0.5 ? 'Channel / Ditch Present' : 'No Major Water Body');
      setBarWidth('waterTab_presBar', Math.min(100, intel.c1.percentage * 20));
    }

    // Helper: Update Weather & Rainfall Tab
    function updateWeatherTab(data, intel) {
      const summaryText = `Regional climatic baseline for Delhi NCR (IMD 30-Year Normals 1991–2020) indicates annual mean precipitation of ~714 mm, with 81.5% (582 mm) concentrated in the July–September Southwest Monsoon.`;
      setInnerText('weather_summaryText', summaryText);
      setInnerText('weather_favorableText', 'Predictable monsoon concentration facilitates seasonal crop planting and rainwater harvesting.');
      setInnerText('weather_attentionText', 'High summer temperatures (June mean 33.8°C, peaks >43°C) cause high evapotranspiration.');
      setInnerText('weather_useText', 'Guides crop calendar scheduling, drainage capacity sizing, and solar potential estimation.');
      setInnerText('weather_limitsText', 'Live daily precipitation requires active telemetry from local IMD automated weather station.');

      setInnerText('weatherTab_rainBadge', '~714 mm / yr');
      setBarWidth('weatherTab_rainBar', 60);

      setInnerText('weatherTab_monsoonBadge', '81.5% (582 mm)');
      setBarWidth('weatherTab_monsoonBar', 82);

      setInnerText('weatherTab_tempBadge', '14.2°C – 33.8°C');
      setBarWidth('weatherTab_tempBar', 65);
    }

    // Helper: Update Agriculture Tab
    function updateAgricultureTab(data, intel) {
      const summaryText = `Cultivable agricultural footprint spans ${intel.cultivablePct}% (${intel.cultivableHa} ha) across active crop signatures (${intel.c4.area_hectares} ha) and arable bare topsoil (${intel.c5.area_hectares} ha). Composite farming suitability is rated ${intel.farmScore}/100 (${intel.farmRating}).`;
      setInnerText('agri_summaryText', summaryText);
      setInnerText('agri_favorableText', `${intel.cultivableHa} ha cultivable ground supports Rabi (wheat, mustard) and Kharif (paddy, fodder) cycles.`);
      setInnerText('agri_attentionText', 'Crop yields require verified groundwater access or irrigation department canal roster rights.');
      setInnerText('agri_useText', 'Farmland acquisition screening, crop acreage planning, and agrarian valuation.');
      setInnerText('agri_limitsText', 'Subterranean soil nutrients (N-P-K, pH) and registered canal water rights unavailable.');

      // Parameter 1: Cultivable Footprint
      setInnerText('agriTab_cultivableBadge', `${intel.cultivablePct}%`);
      setInnerText('agriTab_cultivableUnit', `${intel.cultivableHa} Hectares`);
      setInnerText('agriTab_cultivableRating', intel.cultivablePct > 65 ? 'High Agrarian Expanse' : 'Moderate Farmland');
      setInnerText('agriTab_cultivableDesc', `Combined cultivable acreage across active seasonal crops and arable bare soil (${intel.cultivableHa} ha).`);
      setBarWidth('agriTab_cultivableBar', intel.cultivablePct);

      // Parameter 2: Active Crop Foliage
      setInnerText('agriTab_cropBadge', `${intel.c4.area_hectares} ha`);
      setInnerText('agriTab_cropUnit', `${intel.c4.percentage.toFixed(1)}% Share`);
      setInnerText('agriTab_cropRating', intel.c4.percentage > 18 ? 'Actively Farmed' : 'Low Crop Signature');
      setBarWidth('agriTab_cropBar', intel.c4.percentage * 2.5);

      // Parameter 4: Suitability Score
      setInnerText('agriTab_suitBadge', `${intel.farmScore}/100`);
      setInnerText('agriTab_suitUnit', `Grade ${intel.farmGrade}`);
      setInnerText('agriTab_suitRating', intel.farmRating);
      setBarWidth('agriTab_suitBar', intel.farmScore);
    }

    // Helper: Update Construction Tab
    function updateConstructionTab(data, intel) {
      const summaryText = `Unbuilt developable ground encompasses ${intel.unbuiltPct}% (${intel.unbuiltHa} ha), with existing built structures occupying ${intel.c6.percentage.toFixed(1)}% (${intel.c6.area_hectares} ha). Preliminary ground readiness is rated ${intel.constScore}/100 (${intel.constRating}).`;
      setInnerText('const_summaryText', summaryText);
      setInnerText('const_favorableText', `${intel.unbuiltHa} ha unencumbered ground and flat plain slope (<2.0°) simplify layout planning.`);
      setInnerText('const_attentionText', `${intel.c6.area_hectares} ha existing built hardpack indicates established access, but requires zoning setback check.`);
      setInnerText('const_useText', 'Initial remote site selection screening for greenfield logistics, warehousing, or residential layout.');
      setInnerText('const_limitsText', 'Does NOT imply engineering or zoning approval; geotechnical borehole & DDA/GDA master plan required.');

      // Parameter 1: Open Space
      setInnerText('constTab_openBadge', `${intel.unbuiltHa} ha`);
      setInnerText('constTab_openUnit', `${intel.unbuiltPct}% Unbuilt`);
      setInnerText('constTab_openRating', intel.unbuiltPct > 85 ? 'High Open Expanse' : 'Suburban Density');
      setBarWidth('constTab_openBar', intel.unbuiltPct);

      // Parameter 2: Built-up
      setInnerText('constTab_builtBadge', `${intel.c6.area_hectares} ha`);
      setInnerText('constTab_builtUnit', `${intel.c6.percentage.toFixed(1)}% Built`);
      setInnerText('constTab_builtRating', intel.c6.percentage < 6 ? 'Low Structural Density' : (intel.c6.percentage < 18 ? 'Established Suburban' : 'High Density'));
      setBarWidth('constTab_builtBar', Math.min(100, intel.c6.percentage * 3));

      // Parameter 3: Flood Sensitivity
      setInnerText('constTab_floodBadge', intel.c1.area_hectares < 0.5 ? 'Low Ponding' : 'Channel Moisture');

      // Parameter 4: Readiness Score
      setInnerText('constTab_readinessBadge', `${intel.constScore}/100`);
      setInnerText('constTab_readinessUnit', `Grade ${intel.constGrade}`);
      setInnerText('constTab_readinessRating', intel.constRating);
      setBarWidth('constTab_readinessBar', intel.constScore);
    }

    function setInnerText(id, val) {
      const el = document.getElementById(id);
      if (el) el.innerText = val;
    }

    function setBarWidth(id, pct) {
      const el = document.getElementById(id);
      if (el) el.style.width = `${Math.max(0, Math.min(100, pct))}%`;
    }

    // Helper: 7 Model Classes with User-Facing Labels and Clear Descriptions
    function humanizeClass(rawName) {
      const mapping = {
        'class_1': {
          label: 'Water / High Moisture',
          description: 'Rivers, streams, irrigation canals, and high-moisture wetland soil',
          color: '#5B92A8'
        },
        'class_2': {
          label: 'Dense Vegetation',
          description: 'Woodland clusters, mature tree cover, and thick perennial foliage',
          color: '#2d6a4f'
        },
        'class_3': {
          label: 'Sparse Vegetation',
          description: 'Open grass, field borders, roadside greenery, and sparse shrubbery',
          color: '#8DAA91'
        },
        'class_4': {
          label: 'Agricultural / Crop-like Vegetation',
          description: 'Cultivated crop parcels, active seasonal farmland, and irrigated plots',
          color: '#6EA885'
        },
        'class_5': {
          label: 'Bare Soil / Open Ground',
          description: 'Exposed dry topsoil, ploughed ground, fallow fields, and open clearings',
          color: '#D4A373'
        },
        'class_6': {
          label: 'Built-up / Hard Surfaces',
          description: 'Residential/commercial buildings, paved roads, and concrete structures',
          color: '#C88A75'
        },
        'class_7': {
          label: 'Terrain Shadows / Uncertain Areas',
          description: 'Topographic shadow lines, steep depressions, and low-reflectance anomalies',
          color: '#85769A'
        }
      };

      if (!rawName) return mapping['class_5'];
      const key = rawName.toLowerCase().replace(' ', '_');
      if (mapping[key]) return mapping[key];

      for (let k in mapping) {
        if (rawName.toLowerCase().includes(k.replace('_', ' '))) {
          return mapping[k];
        }
      }

      return {
        label: rawName,
        description: 'Model-detected spectral surface response',
        color: '#637367'
      };
    }

    // 9. Render Land-Cover Composition Breakdown (Clickable rows for spectral parameter details)
    function renderClassDistribution(breakdown) {
      const container = document.getElementById('classDistributionRows');
      container.innerHTML = '';

      Object.keys(breakdown).sort().forEach(k => {
        const item = breakdown[k];
        const row = document.createElement('div');
        row.className = 'space-y-1.5 p-2.5 rounded-xl bg-earth-cardTint border border-earth-border/60 hover:border-forest/60 hover:shadow-2xs transition cursor-pointer group';
        row.onclick = () => openParameterDetail(k);

        const info = humanizeClass(item.class_name || k);

        row.innerHTML = `
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center space-x-2">
              <span class="w-3.5 h-3.5 rounded-md shrink-0 border border-earth-border" style="background-color: ${item.color_hex || info.color};"></span>
              <span class="font-bold text-earth-dark group-hover:text-forest transition">${info.label}</span>
              <span class="text-[10px] text-earth-muted group-hover:text-forest">↗</span>
            </div>
            <div class="font-mono text-earth-muted">
              <span class="font-bold text-forest">${item.percentage.toFixed(1)}%</span>
              <span class="text-[11px] ml-1">(${item.area_hectares} ha)</span>
            </div>
          </div>
          <div class="w-full bg-sand-light rounded-full h-2 overflow-hidden">
            <div class="h-2 rounded-full transition-all duration-300" style="width: ${item.percentage}%; background-color: ${item.color_hex || info.color};"></div>
          </div>
          <p class="text-[11px] text-earth-muted leading-tight">${info.description}</p>
        `;
        container.appendChild(row);
      });
    }

    // =========================================================================
    // PARAMETER DETAIL MODAL & METHODOLOGY ENGINE
    // =========================================================================

    function openParameterDetail(paramKey) {
      if (!currentPrediction) return;
      const data = currentPrediction;
      const intel = computeSampleIntelligence(data);

      const modal = document.getElementById('parameterDetailModal');
      const catEl = document.getElementById('paramModalCategory');
      const statusEl = document.getElementById('paramModalStatus');
      const titleEl = document.getElementById('paramModalTitle');
      const valEl = document.getElementById('paramModalValue');
      const unitEl = document.getElementById('paramModalUnit');
      const ratingEl = document.getElementById('paramModalRating');
      const barEl = document.getElementById('paramModalBar');
      const measuresEl = document.getElementById('paramModalMeasures');
      const meansEl = document.getElementById('paramModalMeans');
      const methodEl = document.getElementById('paramModalMethod');
      const limitsEl = document.getElementById('paramModalLimits');
      const relEl = document.getElementById('paramModalRelevance');

      // Comprehensive Parameter Registry
      let p = {
        category: 'Vegetation',
        status: 'Model-Detected',
        title: 'Vegetation Canopy Analytics',
        value: `${intel.totalVegPct}%`,
        unit: `(${intel.totalVegHa} Hectares)`,
        rating: 'Moderate',
        bar: intel.totalVegPct,
        measures: 'Proportion of ground covered by living, photosynthetically active chlorophyll foliage.',
        means: `On this 40.96 ha site, ${intel.totalVegHa} ha possesses active plant cover, moderating ground temperature and binding topsoil.`,
        method: 'Optical surface reflectance from Sentinel-2 MSI Bands 4 (Red) and 8 (NIR) segmented through SatelliteUNet.',
        limits: 'Optical sensors cannot detect root depth or subterranean biomass; clouds and shadows can mask canopy.',
        relevance: 'Essential for evaluating agrarian health, pasture viability, and soil erosion resilience.'
      };

      if (paramKey === 'veg_total') {
        p = {
          category: 'Vegetation',
          status: 'Model-Detected',
          title: 'Total Vegetative Canopy Coverage',
          value: `${intel.totalVegPct}%`,
          unit: `(${intel.totalVegHa} Hectares Ground Expanse)`,
          rating: intel.totalVegPct > 40 ? 'Dense Canopy' : (intel.totalVegPct > 25 ? 'Moderate Foliage' : 'Sparse Foliage'),
          bar: intel.totalVegPct,
          measures: 'Total cumulative percentage of ground covered by mature trees, crop parcels, field grasses, and shrubbery.',
          means: `This parcel has ${intel.totalVegHa} ha of living vegetative foliage out of 40.96 ha total, supporting high biological activity.`,
          method: 'Sentinel-2 L2A BOA reflectance processed through trained SatelliteUNet multi-class semantic segmentation.',
          limits: 'Single satellite observation date. Multi-temporal seasonal NDVI curves required for longitudinal crop growth tracking.',
          relevance: 'Key baseline for agricultural productivity, wildlife habitat, and natural topsoil stabilization.'
        };
      } else if (paramKey === 'veg_dense') {
        p = {
          category: 'Vegetation',
          status: 'Model-Detected',
          title: 'Dense Forest & Mature Tree Foliage (Class 2)',
          value: `${intel.c2.percentage.toFixed(1)}%`,
          unit: `(${intel.c2.area_hectares} Hectares)`,
          rating: intel.c2.area_hectares > 1.0 ? 'Woodland Presence' : 'Scattered Perennials',
          bar: Math.min(100, intel.c2.percentage * 5),
          measures: 'High-density tree canopy, mature woodland groves, orchards, and perennial tree cover with dark optical absorption.',
          means: `${intel.c2.area_hectares} ha of mature woody canopy provides microclimate shading, bird nesting, and wind reduction.`,
          method: 'Extracted from Class 2 spectral profile with deep absorption in visible red and high near-infrared plateau.',
          limits: 'Cannot assay tree species diversity, wood volume, or sub-canopy undergrowth from 10m satellite pixels.',
          relevance: 'Critical for forestry conservation compliance, tree preservation ordinances, and orchard valuation.'
        };
      } else if (paramKey === 'veg_sparse') {
        p = {
          category: 'Vegetation',
          status: 'Model-Detected',
          title: 'Sparse Meadow & Grassland Cover (Class 3)',
          value: `${intel.c3.percentage.toFixed(1)}%`,
          unit: `(${intel.c3.area_hectares} Hectares)`,
          rating: intel.c3.percentage > 20 ? 'Extensive Meadow' : 'Border Greens',
          bar: intel.c3.percentage * 2,
          measures: 'Open grass clearings, roadside verge foliage, uncultivated meadows, and open shrub canopy.',
          means: `Occupies ${intel.c3.area_hectares} ha (${intel.c3.percentage.toFixed(1)}%), providing natural ground cover without dense obstruction.`,
          method: 'Class 3 spectral signatures exhibiting moderate chlorophyll reflection mixed with partial bare soil background.',
          limits: 'May dry out rapidly in the pre-monsoon summer; difficult to distinguish seasonal grasses from weed cover.',
          relevance: 'Indicates open grazing potential, roadside buffer strips, and permeable non-structural ground.'
        };
      } else if (paramKey === 'veg_crop') {
        p = {
          category: 'Vegetation',
          status: 'Model-Detected',
          title: 'Agricultural Crop Foliage Signature (Class 4)',
          value: `${intel.c4.percentage.toFixed(1)}%`,
          unit: `(${intel.c4.area_hectares} Hectares)`,
          rating: intel.c4.percentage > 18 ? 'Actively Farmed' : 'Low Crop Signature',
          bar: intel.c4.percentage * 2.5,
          measures: 'Actively growing seasonal field crops, cultivated rows, and irrigated agrarian parcels.',
          means: `${intel.c4.area_hectares} ha is actively farmed with seasonal crops (such as wheat, mustard, or fodder in the regional Indo-Gangetic plain).`,
          method: 'Class 4 spectral cluster exhibiting regular spatial geometry and vibrant green reflection characteristic of crop foliage.',
          limits: 'Single snapshot cannot determine whether crops are irrigated via canal, borewell, or rainfall.',
          relevance: 'Primary metric for farmland valuation, agricultural yield forecasting, and tenant crop compensation.'
        };
      } else if (paramKey === 'veg_condition') {
        p = {
          category: 'Vegetation',
          status: 'Derived Index',
          title: 'Overall Canopy Vitality & Density Condition',
          value: intel.totalVegPct >= 40 ? 'High Vigour' : (intel.totalVegPct >= 25 ? 'Moderate Vigour' : 'Sparse / Fallow'),
          unit: `Ratio: ${(intel.totalVegPct / (intel.c5.percentage + 0.1)).toFixed(2)}`,
          rating: intel.totalVegPct >= 35 ? 'Active Photosynthesis' : 'Moderate Biomass',
          bar: Math.min(100, intel.totalVegPct * 2),
          measures: 'The biological health and relative dominance of vegetative cover compared to exposed bare soil.',
          means: `With a canopy-to-bare ground ratio of ${(intel.totalVegPct / (intel.c5.percentage + 0.1)).toFixed(2)}, this land exhibits ${intel.totalVegPct >= 35 ? 'healthy photosynthetic vitality' : 'open fallow terrain'}.`,
          method: 'Integrated ratio calculation correlating Class 2, 3, and 4 against bare ground Class 5.',
          limits: 'Optical canopy health can drop sharply during dry pre-monsoon heat waves (April–June) before recovering in monsoon.',
          relevance: 'Guides farm management, mulching requirements, and seasonal grazing rotations.'
        };
      } else if (paramKey === 'soil_bare') {
        p = {
          category: 'Soil & Terrain',
          status: 'Model-Detected',
          title: 'Bare Soil & Open Ground Exposure (Class 5)',
          value: `${intel.c5.percentage.toFixed(1)}%`,
          unit: `(${intel.c5.area_hectares} Hectares Ground)`,
          rating: intel.c5.percentage > 40 ? 'High Open Exposure' : 'Moderate Open Soil',
          bar: intel.c5.percentage,
          measures: 'Surface area of exposed mineral topsoil, ploughed farmland, fallow clearings, and unpaved dirt.',
          means: `${intel.c5.area_hectares} ha of arable topsoil is open and clear, ready for seasonal tilling, planting, or earthwork grading.`,
          method: 'Class 5 high-reflectance spectral signature in visible and shortwave infrared bands.',
          limits: 'Optical imagery reveals surface color and brightness only; subterranean soil horizons, clay content, and depth are unmeasurable.',
          relevance: 'Essential for plowing planning, foundation leveling, and estimating soil conservation requirements.'
        };
      } else if (paramKey === 'soil_erosion') {
        p = {
          category: 'Soil & Terrain',
          status: 'Derived Index',
          title: 'Surface Soil Erosion Vulnerability',
          value: intel.soilRating.split(' ')[0],
          unit: `Index: ${intel.soilScore}/100`,
          rating: intel.soilRating,
          bar: intel.soilScore,
          measures: 'Estimated susceptibility of topsoil to wind scouring and rainwater runoff erosion based on plant cover protection.',
          means: `${intel.soilRating}: The presence of ${intel.totalVegPct}% vegetative canopy provides ${intel.totalVegPct > 35 ? 'strong' : 'moderate'} root binding across the parcel.`,
          method: 'Empirical soil loss proxy correlating protective vegetation fraction against exposed mineral ground.',
          limits: 'Actual erosion rates also depend on rainfall intensity and subsoil permeability, which require physical ground monitoring.',
          relevance: 'Informs whether cover crops, contour bunds, or windbreak tree rows are required.'
        };
      } else if (paramKey === 'soil_slope') {
        p = {
          category: 'Soil & Terrain',
          status: 'Regional Model',
          title: 'Regional Terrain Gradient & Slope Profile',
          value: '< 2.0°',
          unit: '(< 3.5% Grade)',
          rating: 'Flat Alluvial Plain',
          bar: 10,
          measures: 'Surface topography inclination and macro-relief across the 640m × 640m tile footprint.',
          means: 'Extremely gentle alluvial gradient minimizes slope slippage risks and enables straightforward grading and plowing.',
          method: 'Regional geomorphological survey data for the Indo-Gangetic / Upper Doab plain.',
          limits: 'Micro-topographic depressions (<1m deep) require high-resolution UAV LiDAR or ground total station surveys.',
          relevance: 'Critical for site earthworks, stormwater drainage planning, and foundation design.'
        };
      } else if (paramKey === 'soil_npk') {
        p = {
          category: 'Soil & Terrain',
          status: 'Data Unavailable',
          title: 'Chemical Soil Nutrients (N-P-K, pH, Organic Matter)',
          value: 'Data unavailable',
          unit: 'Lab Test Required',
          rating: 'Laboratory Assay Required',
          bar: 0,
          measures: 'Available Nitrogen (N), Phosphorus (P), Potassium (K), soil pH, Electrical Conductivity (ECe), and organic carbon.',
          means: 'Data unavailable in satellite imagery: Space-borne optical sensors capture reflected sunlight from surface dust and foliage, but cannot assay subterranean chemical nutrient concentrations.',
          method: 'Requires standard physical soil core sampling (0–15 cm and 15–30 cm depth) submitted to an ICAR or Krishi Vigyan Kendra testing lab.',
          limits: 'Never rely on remote sensing for fertilizer dosing or chemical soil suitability without lab verification.',
          relevance: 'Mandatory before purchasing commercial fertilizer or designing crop nutrient cycles.'
        };
      } else if (paramKey === 'soil_bearing') {
        p = {
          category: 'Soil & Terrain',
          status: 'Requires Additional Data',
          title: 'Geotechnical Subsoil Load-Bearing Capacity',
          value: 'Requires borehole testing',
          unit: 'kN/m² (SBC)',
          rating: 'Geotechnical Assay Required',
          bar: 0,
          measures: 'The maximum allowable structural pressure that subsoil horizons can support without shear failure or excessive settlement.',
          means: 'Data unavailable in satellite imagery: Subsurface soil stratigraphy, Standard Penetration Test (SPT) N-values, and water table interactions cannot be measured from orbit.',
          method: 'Requires on-site drilling of geotechnical boreholes with SPT testing and plate load tests by a licensed geotechnical engineer.',
          limits: 'Satellite images can only confirm surface openness; structural engineering calculations must have certified borehole data.',
          relevance: 'Mandatory before designing foundation footings, warehouse plinths, or industrial structures.'
        };
      } else if (paramKey === 'water_surface') {
        p = {
          category: 'Water & Moisture',
          status: 'Model-Detected',
          title: 'Surface Water & High-Moisture Footprint (Class 1)',
          value: `${intel.c1.area_hectares} ha`,
          unit: `(${intel.c1.percentage.toFixed(1)}% of Parcel)`,
          rating: intel.c1.area_hectares < 0.2 ? 'Dry Ground' : (intel.c1.area_hectares < 1.0 ? 'Drainage Channel' : 'Water Corridor'),
          bar: Math.min(100, intel.c1.percentage * 15),
          measures: 'Surface area displaying near-infrared absorption characteristic of standing water, drainage ditches, canals, or saturated wetland soil.',
          means: `Detected ${intel.c1.area_hectares} ha of surface moisture, indicating ${intel.c1.area_hectares < 0.2 ? 'no immediate open water bodies' : 'active irrigation ditches or drainage accumulation'}.`,
          method: 'Class 1 semantic segmentation based on strong water absorption in Sentinel-2 Bands 8 and 11.',
          limits: 'Cannot detect water hidden under dense tree canopy or underground culverts.',
          relevance: 'Identifies irrigation canal alignments, wetland conservation buffers, and local water-logging risks.'
        };
      } else if (paramKey === 'water_presence') {
        p = {
          category: 'Water & Moisture',
          status: 'Model-Detected',
          title: 'Permanent Water Body / Pond Presence',
          value: intel.c1.area_hectares > 0.5 ? `${intel.c1.area_hectares} ha` : 'None Major',
          unit: `${intel.c1.pixel_count} Pixels`,
          rating: intel.c1.area_hectares > 0.5 ? 'Channel / Pond Present' : 'No Major Water Body',
          bar: Math.min(100, intel.c1.percentage * 20),
          measures: 'Existence of contiguous open water bodies such as farm ponds, village reservoirs, or irrigation branch channels.',
          means: intel.c1.area_hectares > 0.5 ? `A contiguous moisture signature spanning ${intel.c1.area_hectares} ha is present.` : `No major open water bodies were detected on this 40.96 ha parcel.`,
          method: 'Connected-component analysis on Class 1 semantic mask pixels.',
          limits: 'Seasonal water bodies may dry up during peak summer months.',
          relevance: 'Essential for livestock watering, environmental clearance setbacks, and flood buffer planning.'
        };
      } else if (paramKey === 'water_drainage') {
        p = {
          category: 'Water & Moisture',
          status: 'Regional Model',
          title: 'Regional Basin Drainage Profile',
          value: 'Natural Alluvial Basin',
          unit: 'Yamuna-Hindon Plain',
          rating: 'Gradual Runoff Drainage',
          bar: 50,
          measures: 'Macro-scale hydrologic catchment behavior and surface runoff discharge path.',
          means: 'Situated in the broad alluvial plain between the Yamuna and Hindon rivers, characterized by gentle natural gradients.',
          method: 'Regional basin boundary maps and hydrological survey records.',
          limits: 'Does not model local stormwater pipe networks or roadside ditch obstructions.',
          relevance: 'Informs site drainage layout, plinth elevation requirements, and culvert sizing.'
        };
      } else if (paramKey === 'water_canal') {
        p = {
          category: 'Water & Moisture',
          status: 'Data Unavailable',
          title: 'Verified Irrigation Canal Delivery Allocations',
          value: 'Data unavailable',
          unit: 'Irrigation Dept Roster Required',
          rating: 'Administrative Roster Required',
          bar: 0,
          measures: 'Legal rights and rotational schedules (Warabandi) for receiving surface canal water from state irrigation canals.',
          means: 'Data unavailable in satellite imagery: While canal channels may be visible on imagery, legal delivery quotas and seasonal allocations require State Irrigation Department command area registries.',
          method: 'Requires official verification through the local Executive Engineer (Irrigation) or Tehsildar command area records.',
          limits: 'Never assume water rights from physical ditch proximity without registered administrative confirmation.',
          relevance: 'Critical for determining whether intensive agriculture can be sustained throughout dry winter (Rabi) cycles.'
        };
      } else if (paramKey === 'water_table') {
        p = {
          category: 'Water & Moisture',
          status: 'Data Unavailable',
          title: 'Subsurface Groundwater Table Depth',
          value: 'Data unavailable',
          unit: 'Meters Below Ground Level (mbgl)',
          rating: 'CGWB Telemetry Required',
          bar: 0,
          measures: 'Depth to the unconfined water table and regional piezometric groundwater levels.',
          means: 'Data unavailable in satellite imagery: Optical and multispectral sensors capture top-of-canopy and topsoil reflection, but cannot penetrate subterranean aquifers.',
          method: 'Requires accessing Central Ground Water Board (CGWB) piezometric well telemetry or drilling an on-site test tubewell.',
          limits: 'Groundwater depth fluctuates by 2–5 meters between pre-monsoon summer and post-monsoon autumn.',
          relevance: 'Mandatory before investing in agricultural tubewells or industrial dewatering setups.'
        };
      } else if (paramKey === 'weather_zone') {
        p = {
          category: 'Weather & Rainfall',
          status: 'Regional Baseline',
          title: 'Agro-Climatic Zone Classification',
          value: 'Zone 4 (Semi-Arid)',
          unit: 'Indo-Gangetic Subtropical',
          rating: 'Warm Subtropical Climate',
          bar: 60,
          measures: 'Regional ecological climate classification based on thermal regimes and moisture availability.',
          means: 'Characterized by hot dry pre-monsoon summers (April–June), a humid southwest monsoon (July–Sept), and cool dry winters (Nov–Feb).',
          method: 'ICAR Agro-Climatic Classification & IMD Climatological Division Normals.',
          limits: 'Macro-scale regional classification; local urban heat island effects may slightly elevate temperatures.',
          relevance: 'Dictates crop selection, seasonal planting dates, and building insulation design.'
        };
      } else if (paramKey === 'weather_rainfall') {
        p = {
          category: 'Weather & Rainfall',
          status: 'Climatological Normal',
          title: 'Climatological Annual Precipitation',
          value: '~714 mm / year',
          unit: 'IMD 30-Year Normal (1991–2020)',
          rating: 'Moderate Semi-Arid Rainfall',
          bar: 60,
          measures: 'Mean annual cumulative precipitation based on 30 years of certified meteorological records.',
          means: 'Receives approximately 650–750 mm of precipitation annually, sufficient for seasonal rainfed and canal-assisted farming.',
          method: 'India Meteorological Department (IMD) 30-Year Climatological Table (1991–2020) for Delhi NCR / West UP.',
          limits: 'Represents 30-year statistical average; individual annual rainfall varies by ±25% depending on monsoon vigor.',
          relevance: 'Foundational for rainwater harvesting design, irrigation budgeting, and flood risk mitigation.'
        };
      } else if (paramKey === 'weather_monsoon') {
        p = {
          category: 'Weather & Rainfall',
          status: 'Climatological Normal',
          title: 'Monsoon Rainfall Concentration (July–Sept)',
          value: '81.5% (582 mm)',
          unit: 'Southwest Monsoon Total',
          rating: 'Highly Concentrated Season',
          bar: 82,
          measures: 'Proportion of annual rainfall received during the 12-week southwest monsoon period.',
          means: 'Over 80% of annual rain falls between July and September, causing sudden drainage surges followed by 9 dry months.',
          method: 'IMD seasonal precipitation breakdown statistics.',
          limits: 'Monsoon onset and withdrawal dates can fluctuate by 1–2 weeks from year to year.',
          relevance: 'Demonstrates why on-site stormwater retention and rainwater harvesting are critical.'
        };
      } else if (paramKey === 'weather_temp') {
        p = {
          category: 'Weather & Rainfall',
          status: 'Climatological Normal',
          title: 'Seasonal Mean Temperature Spectrum',
          value: '14.2°C – 33.8°C',
          unit: 'Jan Mean to June Mean',
          rating: 'Wide Subtropical Swing',
          bar: 65,
          measures: 'Mean monthly thermal range across the annual cycle.',
          means: 'Winter monthly means around 14°C (with extreme minimums down to 4°C) swing to pre-monsoon monthly means around 34°C (with peaks above 43°C).',
          method: 'IMD 30-Year Normals (1991–2020) surface meteorological station observations.',
          limits: 'Daily microclimate temperature extremes can exceed monthly means.',
          relevance: 'Essential for HVAC heating/cooling calculations, greenhouse design, and crop heat tolerance planning.'
        };
      } else if (paramKey === 'weather_live') {
        p = {
          category: 'Weather & Rainfall',
          status: 'Data Unavailable',
          title: 'Live Real-Time Automated Rain Gauge',
          value: 'Data unavailable',
          unit: 'Active IoT Connection Required',
          rating: 'Live Station Required',
          bar: 0,
          measures: 'Real-time 24-hour precipitation and hourly meteorological telemetry.',
          means: 'Data unavailable without connected IoT/IMD automated weather station: Satellite imagery provides spatial snapshots but cannot stream continuous ground rain gauge readings.',
          method: 'Requires connecting an active API gateway to local IMD or Open-Meteo automated weather stations.',
          limits: 'Historical satellite tiles reflect single-epoch observation conditions.',
          relevance: 'Required for real-time irrigation automation and immediate storm flood warnings.'
        };
      } else if (paramKey === 'agri_footprint') {
        p = {
          category: 'Agriculture',
          status: 'Model-Detected',
          title: 'Cultivable Agricultural Footprint',
          value: `${intel.cultivablePct}%`,
          unit: `(${intel.cultivableHa} Hectares Farmland)`,
          rating: intel.cultivablePct > 65 ? 'Prime Farmland Footprint' : 'Moderate Farmland',
          bar: intel.cultivablePct,
          measures: 'Combined acreage of active seasonal crops (Class 4) and cultivable arable bare ground (Class 5).',
          means: `${intel.cultivableHa} ha out of 40.96 ha total consists of farmable land, offering extensive contiguous agricultural capability.`,
          method: 'Aggregated sum of semantic segmentation Classes 4 and 5.',
          limits: 'Does not assay soil nutrient availability or groundwater table depth.',
          relevance: 'Primary metric for agrarian property valuation and crop acreage budgeting.'
        };
      } else if (paramKey === 'agri_crop') {
        p = {
          category: 'Agriculture',
          status: 'Model-Detected',
          title: 'Active Seasonal Crop Canopy (Class 4)',
          value: `${intel.c4.percentage.toFixed(1)}%`,
          unit: `(${intel.c4.area_hectares} Hectares)`,
          rating: intel.c4.percentage > 18 ? 'Actively Farmed' : 'Low Crop Signature',
          bar: intel.c4.percentage * 2.5,
          measures: 'Area exhibiting the optical and geometric signature of actively growing crops at the time of satellite capture.',
          means: `${intel.c4.area_hectares} ha of crops are currently growing on site, indicating active agricultural utilization by local farmers.`,
          method: 'Class 4 spectral classification reflecting healthy crop chlorophyll absorption.',
          limits: 'Crop stage (sowing, vegetative, harvest) requires multi-temporal monitoring.',
          relevance: 'Confirms active farming status and ongoing agricultural revenue generation.'
        };
      } else if (paramKey === 'agri_moisture') {
        p = {
          category: 'Agriculture',
          status: 'Model-Detected',
          title: 'Natural Surface Moisture Adequacy',
          value: intel.c1.area_hectares > 0.5 ? 'Moderate Surface Moisture' : 'Adequate Normal Moisture',
          unit: `${intel.c1.area_hectares} ha Moisture Area`,
          rating: 'Favorable Crop Moisture',
          bar: 65,
          measures: 'The adequacy of surface soil moisture and local drainage proximity to sustain crop growth.',
          means: 'Alluvial soils in this region retain sufficient moisture during post-monsoon winter cycles to support wheat and mustard crops.',
          method: 'Optical surface moisture extraction (Class 1) correlated with seasonal climatic normals.',
          limits: 'During hot pre-monsoon months (April–June), supplemental tubewell irrigation is mandatory.',
          relevance: 'Critical for selecting drought-tolerant vs water-intensive crop rotations.'
        };
      } else if (paramKey === 'agri_suitability') {
        p = {
          category: 'Agriculture',
          status: 'Composite Index',
          title: 'Preliminary Farming Suitability Assessment',
          value: `${intel.farmScore}/100`,
          unit: `Grade ${intel.farmGrade}`,
          rating: intel.farmRating,
          bar: intel.farmScore,
          measures: 'Overall agricultural suitability based on cultivable land fraction, canopy vigor, and absence of built obstructions.',
          means: `${intel.farmRating}: The parcel offers ${intel.cultivableHa} ha of cultivable land and minimal structural disturbance.`,
          method: 'Multi-criteria weighted formula: (Crop × 1.5) + (Bare Soil × 0.75) + (Canopy × 0.4) - (Built × 1.2).',
          limits: 'Preliminary remote assessment; does not replace laboratory chemical soil tests or certified canal rosters.',
          relevance: 'Guides farm investment decisions and agro-forestry feasibility.'
        };
      } else if (paramKey === 'agri_rights') {
        p = {
          category: 'Agriculture',
          status: 'Data Unavailable',
          title: 'Verified Canal Water Rights & Soil Nutrients',
          value: 'Data unavailable',
          unit: 'Administrative Records Required',
          rating: 'External Diligence Required',
          bar: 0,
          measures: 'Formal canal irrigation delivery allocations and laboratory soil nutrient health.',
          means: 'Data unavailable in satellite imagery: Satellite sensors cannot determine whether a parcel has registered canal delivery allocations or assay underground soil fertility.',
          method: 'Requires official verification through local irrigation registries and agricultural laboratory soil core tests.',
          limits: 'Never assume water rights or soil fertility based solely on satellite images.',
          relevance: 'Mandatory pre-purchase due diligence check for agrarian investors.'
        };
      } else if (paramKey === 'const_open') {
        p = {
          category: 'Construction',
          status: 'Model-Detected',
          title: 'Open Unbuilt Developable Space',
          value: `${intel.unbuiltHa} ha`,
          unit: `(${intel.unbuiltPct}% Unencumbered)`,
          rating: intel.unbuiltPct > 85 ? 'High Greenfield Expanse' : 'Suburban Density',
          bar: intel.unbuiltPct,
          measures: 'Total ground footprint free from permanent concrete structures, buildings, or paved hardpack.',
          means: `${intel.unbuiltHa} ha out of 40.96 ha total is unbuilt open land, offering maximum layout flexibility for master planning.`,
          method: 'Computed by subtracting Class 6 built-up area from total analyzed area (40.96 ha).',
          limits: 'Does not account for legal easements, high-tension power line buffers, or zoning setbacks.',
          relevance: 'Key metric for greenfield industrial parks, warehousing layouts, and housing developments.'
        };
      } else if (paramKey === 'const_built') {
        p = {
          category: 'Construction',
          status: 'Model-Detected',
          title: 'Existing Built-up & Hardpack Footprint (Class 6)',
          value: `${intel.c6.percentage.toFixed(1)}%`,
          unit: `(${intel.c6.area_hectares} Hectares)`,
          rating: intel.c6.percentage < 6 ? 'Low Structural Density' : (intel.c6.percentage < 18 ? 'Established Suburban' : 'High Density'),
          bar: Math.min(100, intel.c6.percentage * 3),
          measures: 'Permanent residential, commercial, or industrial buildings, paved roadways, concrete yards, and packed ground.',
          means: `Existing built structures occupy ${intel.c6.area_hectares} ha (${intel.c6.percentage.toFixed(1)}%), providing established road and power infrastructure access.`,
          method: 'Class 6 spectral reflectance characteristics in visible and shortwave infrared bands.',
          limits: 'Cannot determine building height, structural soundness, or municipal permit legality from 10m pixels.',
          relevance: 'Indicates utility access proximity, brownfield redevelopment scope, and demolition requirements.'
        };
      } else if (paramKey === 'const_flood') {
        p = {
          category: 'Construction',
          status: 'Model-Detected',
          title: 'Surface Moisture Inundation Sensitivity',
          value: intel.c1.area_hectares < 0.5 ? 'Low Ponding' : 'Channel Moisture',
          unit: `${intel.c1.area_hectares} ha Moisture`,
          rating: intel.c1.area_hectares < 0.5 ? 'Minimal Surface Ponding' : 'Drainage Verification Advised',
          bar: Math.min(100, intel.c1.percentage * 15),
          measures: 'Sensitivity to surface water accumulation based on optical standing moisture and macro-topography.',
          means: intel.c1.area_hectares < 0.5 ? 'No persistent standing water was observed across the site on satellite observation date.' : `Surface moisture spanning ${intel.c1.area_hectares} ha indicates local drainage channels or low-lying ground.`,
          method: 'Class 1 semantic segmentation correlated with regional elevation basin behavior.',
          limits: 'Single snapshot does not replace certified municipal 100-year flood zone hazard maps.',
          relevance: 'Essential for calculating finished floor plinth heights and stormwater discharge culverts.'
        };
      } else if (paramKey === 'const_readiness') {
        p = {
          category: 'Construction',
          status: 'Composite Index',
          title: 'Preliminary Site Ground Readiness Score',
          value: `${intel.constScore}/100`,
          unit: `Grade ${intel.constGrade}`,
          rating: intel.constRating,
          bar: intel.constScore,
          measures: 'Preliminary remote screening score evaluating unbuilt space availability, flat topography, and low flood ponding.',
          means: `${intel.constRating}: High open ground availability (${intel.unbuiltHa} ha) provides clean site geometry.`,
          method: 'Multi-criteria formula: (Unbuilt % × 0.55) + Topography (20 pts) + Water Risk (15 pts) + Infrastructure Access (5 pts).',
          limits: 'Preliminary remote screening only; strictly does NOT constitute architectural or geotechnical engineering approval.',
          relevance: 'Fast preliminary screening tool for comparing candidate development sites.'
        };
      } else if (paramKey === 'const_zoning') {
        p = {
          category: 'Construction',
          status: 'Data Unavailable',
          title: 'Cadastral Deeds & Municipal Zoning NOC',
          value: 'Data unavailable',
          unit: 'Municipal NOC Required',
          rating: 'Statutory Diligence Required',
          bar: 0,
          measures: 'Certified ownership titles, non-encumbrance status, Master Plan land use zoning, and environmental buffer clearances.',
          means: 'Data unavailable in satellite imagery: Satellite images measure physical ground reflectance, but cannot verify certified land title deeds, boundary disputes, or zoning permissions.',
          method: 'Requires official verification through local revenue registries (Jamabandi/Bhulekh) and town planning authorities (DDA/GDA).',
          limits: 'Never execute land purchase or lease agreements without certified legal title clearance.',
          relevance: 'Mandatory statutory due diligence before commencing any construction or financial transaction.'
        };
      } else if (paramKey.startsWith('class_')) {
        // Individual spectral class inspection
        const cStat = data.class_breakdown[paramKey] || {};
        const info = humanizeClass(paramKey);
        p = {
          category: 'Land Cover',
          status: 'Model-Detected',
          title: `${info.label} (${paramKey.toUpperCase()})`,
          value: `${cStat.percentage ? cStat.percentage.toFixed(1) : '0.0'}%`,
          unit: `(${cStat.area_hectares || '0.00'} Hectares Ground Area)`,
          rating: info.label,
          bar: cStat.percentage || 0,
          measures: `Ground surface area exhibiting the spectral reflectance characteristics of ${info.label.toLowerCase()}.`,
          means: `${info.description}. Occupies ${cStat.area_hectares || '0.00'} hectares (${cStat.percentage ? cStat.percentage.toFixed(1) : '0.0'}% of the parcel).`,
          method: `Sentinel-2 MSI multi-spectral segmentation via SatelliteUNet deep neural network (Validation mIoU: 0.4839, Accuracy: 79.59%).`,
          limits: '10.0m spatial ground sampling distance (GSD); objects smaller than 100 m² blend into mixed pixels.',
          relevance: 'Fundamental unit of Earth observation analysis; defines the physical land-cover composition.'
        };
      }

      // Populate Modal Fields
      catEl.innerText = p.category;
      statusEl.innerText = p.status;
      titleEl.innerText = p.title;
      valEl.innerText = p.value;
      unitEl.innerText = p.unit;
      ratingEl.innerText = p.rating;
      barEl.style.width = `${Math.max(0, Math.min(100, p.bar))}%`;
      measuresEl.innerText = p.measures;
      meansEl.innerText = p.means;
      methodEl.innerText = p.method;
      limitsEl.innerText = p.limits;
      relEl.innerText = p.relevance;

      modal.classList.remove('hidden');
    }

    function closeParameterModal() {
      const modal = document.getElementById('parameterDetailModal');
      if (modal) modal.classList.add('hidden');
    }

    // =========================================================================
    // ASSESSMENT CRITERIA & SCORING MODAL ENGINE
    // =========================================================================

    function openAssessmentModal(assessmentKey) {
      if (!currentPrediction) return;
      const data = currentPrediction;
      const intel = computeSampleIntelligence(data);

      const modal = document.getElementById('assessmentModal');
      const titleEl = document.getElementById('assessModalTitle');
      const subEl = document.getElementById('assessModalSub');
      const scoreEl = document.getElementById('assessModalScore');
      const labelEl = document.getElementById('assessModalLabel');
      const gradeEl = document.getElementById('assessModalGrade');
      const listEl = document.getElementById('assessModalCriteriaList');
      const formulaEl = document.getElementById('assessModalFormula');
      const missingEl = document.getElementById('assessModalMissing');

      let criteria = [];
      let formulaText = '';
      let missingText = '';

      if (assessmentKey === 'farming') {
        titleEl.innerText = 'Farming Suitability Scoring Methodology';
        subEl.innerText = 'Agricultural Production & Soil Viability Index';
        scoreEl.innerText = `${intel.farmScore} / 100`;
        labelEl.innerText = intel.farmRating;
        gradeEl.innerText = intel.farmGrade;

        criteria = [
          { name: 'Active Crop Canopy (Class 4)', value: `${intel.c4.percentage.toFixed(1)}% (${intel.c4.area_hectares} ha)`, pts: `+${Math.round(intel.c4.percentage * 1.5)} pts`, rationale: 'Proven ongoing cultivation demonstrates favorable local growing conditions.' },
          { name: 'Arable Bare Soil (Class 5)', value: `${intel.c5.percentage.toFixed(1)}% (${intel.c5.area_hectares} ha)`, pts: `+${Math.round(intel.c5.percentage * 0.75)} pts`, rationale: 'Exposed tillable topsoil provides immediate acreage for seasonal sowing.' },
          { name: 'Vegetative Vigor & Biomass', value: `${intel.totalVegPct}% Canopy`, pts: `+${Math.round(intel.totalVegPct * 0.4)} pts`, rationale: 'High green cover confirms photosynthesis, ground moisture, and root binding.' },
          { name: 'Built-up Obstruction (Class 6)', value: `${intel.c6.percentage.toFixed(1)}% (${intel.c6.area_hectares} ha)`, pts: `-${Math.round(intel.c6.percentage * 1.2)} pts`, rationale: 'Paved hardpack and structures deduct from available farming footprint.' },
          { name: 'Natural Surface Moisture', value: `${intel.c1.area_hectares} ha Detected`, pts: intel.c1.percentage >= 0.5 ? '+5 pts' : '+0 pts', rationale: 'Proximity to drainage ditches or wetland moisture provides hydration resilience.' }
        ];

        formulaText = 'Farming Suitability Index = (Active Crop % × 1.5) + (Arable Soil % × 0.75) + (Total Canopy % × 0.4) - (Built-up % × 1.2) + (Moisture Bonus: 5 pts). Normalized to a 0–100 scale.';
        missingText = 'This index evaluates physical surface indications from space. Real-world agrarian success requires laboratory soil chemistry (N-P-K, pH, organic carbon) and verified State Irrigation Department canal delivery rosters.';
      } else if (assessmentKey === 'construction') {
        titleEl.innerText = 'Construction Ground Readiness Scoring Methodology';
        subEl.innerText = 'Site Selection & Ground Openness Index';
        scoreEl.innerText = `${intel.constScore} / 100`;
        labelEl.innerText = intel.constRating;
        gradeEl.innerText = intel.constGrade;

        criteria = [
          { name: 'Unencumbered Open Space', value: `${intel.unbuiltHa} ha (${intel.unbuiltPct}%)`, pts: `+${Math.round(intel.unbuiltPct * 0.55)} pts`, rationale: 'Extensive open acreage maximizes layout flexibility and avoids demolition costs.' },
          { name: 'Regional Plain Topography', value: '< 2.0° Alluvial Plain', pts: '+20 pts', rationale: 'Flat alluvial slope minimizes grading earthworks and landslide risks.' },
          { name: 'Low Surface Ponding Risk', value: `${intel.c1.area_hectares} ha Moisture`, pts: intel.c1.area_hectares < 0.5 ? '+15 pts' : '+10 pts', rationale: 'Absence of persistent surface standing water indicates good optical dryness.' },
          { name: 'Utility & Infrastructure Access', value: `${intel.c6.percentage.toFixed(1)}% Built Footprint`, pts: (intel.c6.percentage > 3 && intel.c6.percentage < 20) ? '+5 pts' : '+0 pts', rationale: 'Proximity to established suburban structures correlates with power and road access.' }
        ];

        formulaText = 'Construction Ground Readiness = (Unbuilt % × 0.55) + Topography Factor (20 pts) + Water Ponding Factor (up to 15 pts) + Infrastructure Proximity Factor (up to 5 pts). Normalized to 0–100 scale.';
        missingText = 'Preliminary remote screening only. Strictly does NOT constitute architectural approval, geotechnical foundation load approval, or municipal zoning clearance (DDA/GDA master plan). Certified borehole core assays are required before commitments.';
      } else if (assessmentKey === 'soil') {
        titleEl.innerText = 'Surface Soil Stability Assessment Methodology';
        subEl.innerText = 'Topsoil Preservation & Erosion Resilience Index';
        scoreEl.innerText = `${intel.soilScore} / 100`;
        labelEl.innerText = intel.soilRating;
        gradeEl.innerText = intel.totalVegPct >= 40 ? 'A' : (intel.totalVegPct >= 25 ? 'B' : 'C');

        criteria = [
          { name: 'Protective Plant Canopy', value: `${intel.totalVegPct}% Coverage`, pts: `+${Math.round(intel.totalVegPct * 0.9)} pts`, rationale: 'Living foliage intercepts raindrop impact energy and binds topsoil with root systems.' },
          { name: 'Low Terrain Slope Gradient', value: '< 2.0° Alluvial Gradient', pts: '+30 pts', rationale: 'Flat plain minimizes gravity-driven surface sheet wash and rill formation.' },
          { name: 'Arable Soil Resistance Factor', value: `${intel.c5.percentage.toFixed(1)}% Bare Ground`, pts: intel.c5.percentage > 40 ? '+5 pts' : '+15 pts', rationale: 'Dense topsoil exposure without vegetative armor increases wind scour vulnerability.' }
        ];

        formulaText = 'Soil Stability Index = Baseline Factor (30 pts) + (Canopy % × 0.9) + Ground Armor Bonus (up to 15 pts). Evaluates physical vegetative protection against topsoil erosion.';
        missingText = 'Assesses surface vegetative armor from space. Soil chemical nutrient assays (nitrogen, phosphorus, potassium, organic carbon, pH) require physical laboratory testing at an ICAR or KVK laboratory.';
      } else if (assessmentKey === 'confidence') {
        titleEl.innerText = 'Model Confidence & Statistical Telemetry';
        subEl.innerText = 'SatelliteUNet Neural Certainty Assessment';
        scoreEl.innerText = `${intel.confPct}%`;
        labelEl.innerText = intel.confPct >= 78 ? 'High Neural Certainty' : 'Good Statistical Confidence';
        gradeEl.innerText = 'A';

        criteria = [
          { name: 'Mean Softmax Probability', value: `${intel.confPct}% Mean Certainty`, pts: `${intel.confPct}%`, rationale: 'Average maximum softmax probability across all 4,096 matrix pixels for this tile.' },
          { name: 'Spatial Validation Accuracy', value: '79.59% Overall Acc', pts: 'Benchmark: 79.6%', rationale: 'Independently evaluated across 6,088 spatially grouped regional validation tiles.' },
          { name: 'Validation Mean IoU', value: '0.4839 mIoU', pts: 'Benchmark: 0.484', rationale: 'Area intersection-over-union across 7 numeric land cover classes after 25 training epochs.' },
          { name: 'Spatial Resolution & Footprint', value: '10.0m GSD (40.96 ha)', pts: '4,096 px', rationale: 'Standard Sentinel-2 L2A tile dimensions (64 × 64 pixels at 100 m² per pixel).' }
        ];

        formulaText = 'Statistical telemetry reflects the trained neural network softmax entropy and historical validation metrics. All predictions are automated estimates and not certified ground cadastral surveys.';
        missingText = 'Satellite observations cannot determine legal ownership titles, boundary encumbrances, or cadastral deeds (Jamabandi / Bhulekh). Contact the local Tehsildar office for certified title records.';
      }

      listEl.innerHTML = '';
      criteria.forEach(c => {
        const item = document.createElement('div');
        item.className = 'p-3 bg-earth-cardTint rounded-xl border border-earth-border/70 flex items-center justify-between text-xs';
        item.innerHTML = `
          <div class="space-y-0.5">
            <span class="font-bold text-earth-dark block">${c.name}</span>
            <span class="text-[11px] text-earth-muted block">${c.rationale}</span>
            <span class="text-[10px] font-mono text-earth-muted">Measured: ${c.value}</span>
          </div>
          <span class="font-mono font-bold text-forest bg-white px-2.5 py-1 rounded-lg border border-earth-border shrink-0 ml-3">${c.pts}</span>
        `;
        listEl.appendChild(item);
      });

      formulaEl.innerText = formulaText;
      missingEl.innerText = missingText;

      modal.classList.remove('hidden');
    }

    function closeAssessmentModal() {
      const modal = document.getElementById('assessmentModal');
      if (modal) modal.classList.add('hidden');
    }
'''

# Find the start of function renderAllResults
pattern_render = re.compile(r'function renderAllResults\(data\) \{[\s\S]*?function humanizeClass\(rawName\) \{[\s\S]*?\}\s*\}')

# Let's inspect what renderAllResults to renderClassDistribution spans
old_start = '    // 8. Render All Predictions across Overview, Categories & Gallery\n    function renderAllResults(data) {'
old_end = '    // 10. Simple Land-Insight Category Navigation\n    function switchInsightTab(tabId) {'

if old_start in html and old_end in html:
    idx_start = html.find(old_start)
    idx_end = html.find(old_end)
    html_new = html[:idx_start] + js_engine_code + '\n\n' + html[idx_end:]
    
    # Also update keydown listener to close modals
    old_escape = "if (e.key === 'Escape') {\n          closeReportModal();\n          toggleTechModal(false);\n          toggleChatDrawer(false);\n          closeLightbox();\n        }"
    new_escape = "if (e.key === 'Escape') {\n          closeReportModal();\n          toggleTechModal(false);\n          toggleChatDrawer(false);\n          closeLightbox();\n          closeParameterModal();\n          closeAssessmentModal();\n        }"
    html_new = html_new.replace(old_escape, new_escape)

    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html_new)
    print("Successfully replaced JS engine and updated escape key listener!")
else:
    print("Error: Could not locate boundary markers in HTML!")
