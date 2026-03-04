import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ItemService } from '../../services/item.service';
import { OutfitService } from '../../services/outfit.service';

// Match quality → human readable hint for the UI
const MATCH_LABELS: Record<string, { label: string; color: string }> = {
  exact:   { label: '✦ Perfect match',   color: '#4caf50' },
  any:     { label: '◎ Best available',  color: '#ff9800' },
  missing: { label: '✕ Not in wardrobe', color: '#f44336' },
};

function matchLabel(quality: string): { label: string; color: string } {
  if (!quality) return MATCH_LABELS['any'];
  if (quality === 'exact') return MATCH_LABELS['exact'];
  if (quality === 'missing') return MATCH_LABELS['missing'];
  // weather~X, style~X, style~X+weather~Y → partial match
  return { label: `≈ ${quality.replace(/~/g, ': ').replace(/\+/g, ' · ')}`, color: '#2196f3' };
}

@Component({
  selector: 'app-outfit',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './outfit.component.html',
  styleUrl: './outfit.component.css',
})
export class OutfitComponent implements OnInit {
  styles  = ['Casual', 'Formal', 'Streetwear', 'Bohemian', 'Sporty', 'Elegant', 'Vintage', 'Minimalist'];
  weathers = ['Summer', 'Winter', 'Transitional'];
  genders  = ["Men's", "Women's", 'Unisex'];

  selectedStyle:   string = 'Casual';
  selectedWeather: string = 'Summer';
  selectedGender:  string = "Men's";

  isLoading: boolean = false;
  errorMessage: string = '';
  timestamp: number = Date.now();

  slotsLayout = [
    { col: 1, id: 'sombrero',    category: 'hats',        icon: '🎩' },
    { col: 1, id: 'gafas',       category: 'sunglasses',  icon: '🕶️' },
    { col: 1, id: 'joyeria',     category: 'jewellery',   icon: '💍' },
    { col: 1, id: 'accesorios',  category: 'accessories', icon: '🧣' },
    { col: 2, id: 'camiseta',    category: 'tops',        icon: '👕' },
    { col: 2, id: 'cuerpoentero',category: 'all-body',    icon: '👗' },
    { col: 2, id: 'pantalones',  category: 'bottoms',     icon: '👖' },
    { col: 2, id: 'zapatos',     category: 'shoes',       icon: '👟' },
    { col: 3, id: 'chaqueta',    category: 'outerwear',   icon: '🧥' },
    { col: 3, id: 'bolso',       category: 'bags',        icon: '👜' },
    { col: 3, id: 'bufanda',     category: 'scarves',     icon: '🧣' },
  ];

  outfit: Record<string, any> = {};
  locked: Record<string, boolean> = {};

  constructor(private itemService: ItemService, private outfitService: OutfitService, private cdr: ChangeDetectorRef) {
    this.slotsLayout.forEach(s => {
      this.outfit[s.id] = null;
      this.locked[s.id] = false;
    });
  }

  ngOnInit() {}

  private categoryToSlot(category: string): string | null {
    const slot = this.slotsLayout.find(s => s.category === category);
    return slot ? slot.id : null;
  }

  getMatchInfo(slotId: string): { label: string; color: string } | null {
    const item = this.outfit[slotId];
    if (!item) return null;
    return matchLabel(item.match_quality);
  }

  onGenerar() {
    this.isLoading = true;
    this.errorMessage = '';

    this.itemService.getRecommendation(
      this.selectedStyle,
      this.selectedWeather,
      this.selectedGender
    ).subscribe({
      next: (response: any) => {
        this.isLoading = false;
        this.timestamp = Date.now();

        // Build a fresh outfit object — replacing the reference triggers Angular change detection
        const newOutfit: Record<string, any> = {};
        this.slotsLayout.forEach(s => {
          newOutfit[s.id] = this.locked[s.id] ? this.outfit[s.id] : null;
        });

        const anchorSlotId = this.categoryToSlot(response.anchor_category);
        if (anchorSlotId && !this.locked[anchorSlotId]) {
          newOutfit[anchorSlotId] = {
            id: response.anchor_item_id,
            image_path: response.anchor_image_path,
            category: response.anchor_category,
            compatibility_score: 1.0,
            match_quality: 'exact',
          };
        }

        response.outfit.forEach((item: any) => {
          const slotId = this.categoryToSlot(item.category);
          if (slotId && !this.locked[slotId]) {
            newOutfit[slotId] = item.item_id ? {
              id: item.item_id,
              image_path: item.image_path,
              category: item.category,
              compatibility_score: item.compatibility_score,
              match_quality: item.match_quality,
            } : null;
          }
        });

        this.outfit = newOutfit;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        if (err.status === 404) {
          this.errorMessage = 'No tienes prendas procesadas en tu armario. Sube algunas prendas primero.';
        } else if (err.status === 503) {
          this.errorMessage = 'El motor de recomendación no está disponible.';
        } else {
          this.errorMessage = 'Error al generar el outfit. Inténtalo de nuevo.';
        }
      }
    });
  }

  onRandomizeSingle(slotId: string) {
    if (this.locked[slotId]) return;
    // Re-generate while keeping all other slots locked
    const prevLocked = { ...this.locked };
    this.slotsLayout.forEach(s => {
      if (s.id !== slotId) this.locked[s.id] = true;
    });
    this.onGenerar();
    // Restore lock state after call
    this.locked = prevLocked;
    this.locked[slotId] = false;
  }

  toggleLock(slotId: string) {
    this.locked[slotId] = !this.locked[slotId];
  }

  onConfirmar() {
    const itemIdsToDirty: string[] = [];
    const snapshot: any[] = [];

    for (const slot of this.slotsLayout) {
      const item = this.outfit[slot.id];
      if (item?.id) {
        itemIdsToDirty.push(item.id);
        snapshot.push({
          slot_id: slot.id,
          item_id: item.id,
          category: item.category,
          image_path: item.image_path,
          compatibility_score: item.compatibility_score,
          match_quality: item.match_quality,
        });
      }
    }

    if (snapshot.length === 0) {
      alert('No hay prendas seleccionadas para confirmar.');
      return;
    }

    const payload = {
      style: this.selectedStyle,
      weather: this.selectedWeather,
      gender: this.selectedGender,
      items_snapshot: snapshot,
      item_ids_to_dirty: itemIdsToDirty,
    };

    this.outfitService.saveOutfit(payload).subscribe({
      next: () => {
        // Reset all slots
        const cleared: Record<string, any> = {};
        this.slotsLayout.forEach(s => {
          cleared[s.id] = null;
          this.locked[s.id] = false;
        });
        this.outfit = cleared;
        this.cdr.detectChanges();
      },
      error: () => alert('Error al guardar el outfit.')
    });
  }
}