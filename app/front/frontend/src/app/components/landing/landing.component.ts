import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { OutfitService } from '../../services/outfit.service';
import { ItemService } from '../../services/item.service';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './landing.component.html',
  styleUrl: './landing.component.css',
})
export class LandingComponent implements OnInit {
  outfits: any[] = [];
  items: any[] = [];
  isLoading = true;
  isCleaning: boolean = false;

  // Lightbox
  lightboxOutfit: any = null;
  outfitToDelete: any = null;

  constructor(
    private outfitService: OutfitService,
    private itemService: ItemService,
    private cdr: ChangeDetectorRef,
  ) {}

  ngOnInit() {
    this.loadAll();
  }

  loadAll() {
    this.isLoading = true;
    this.itemService.getItems().subscribe(items => {
      this.items = items;
      this.outfitService.getOutfits().subscribe(outfits => {
        this.outfits = outfits;
        this.isLoading = false;
        this.cdr.detectChanges();
      });
    });
  }

  get totalItems() { return this.items.length; }
  get cleanItems() { return this.items.filter(i => i.clean).length; }
  get dirtyItems() { return this.items.filter(i => !i.clean).length; }
  get cleanPct() { return this.totalItems ? Math.round(100 * this.cleanItems / this.totalItems) : 0; }
  get totalOutfits() { return this.outfits.length; }

  get categoryBreakdown(): { label: string; count: number; pct: number }[] {
    const counts: Record<string, number> = {};
    this.items.forEach(i => {
      if (i.category) counts[i.category] = (counts[i.category] || 0) + 1;
    });
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([label, count]) => ({
        label,
        count,
        pct: Math.round(100 * count / this.totalItems),
      }));
  }

  get mostWornStyle(): string {
    const counts: Record<string, number> = {};
    this.outfits.forEach(o => {
      counts[o.style] = (counts[o.style] || 0) + 1;
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? '—';
  }

  getOutfitImages(outfit: any): string[] {
    return (outfit.items_snapshot || [])
      .filter((s: any) => s.image_path)
      .slice(0, 4)
      .map((s: any) => s.image_path);
  }

  formatDate(iso: string): string {
    return new Date(iso).toLocaleDateString('es-ES', {
      day: 'numeric', month: 'short', year: 'numeric'
    });
  }
  openLightbox(outfit: any) {
    this.lightboxOutfit = outfit;
  }

  closeLightbox() {
    this.lightboxOutfit = null;
  }



  cleanOutfitItems() {
    if (!this.lightboxOutfit || !this.lightboxOutfit.items_snapshot) return;

    const itemsToClean = this.lightboxOutfit.items_snapshot
      .filter((slot: any) => slot.item_id) 
      .map((slot: any) => slot.item_id);

    if (itemsToClean.length === 0) return;

    this.isCleaning = true;

    const updateRequests = itemsToClean.map((id: string) =>
      this.itemService.updateItem(id, { limpio: true })
    );

    forkJoin(updateRequests).subscribe({
      next: () => {
        this.isCleaning = false;
        this.loadAll(); 
      },
      error: (err) => {
        this.isCleaning = false;
        console.error(err);
      }
    });
  }

  deleteOutfit(outfit: any) {
    this.outfitToDelete = outfit;
  }

  confirmDelete() {
    if (!this.outfitToDelete) return;
    
    this.outfitService.deleteOutfit(this.outfitToDelete.id).subscribe(() => {
      this.outfits = this.outfits.filter(o => o.id !== this.outfitToDelete.id);
      this.outfitToDelete = null; 
      this.cdr.detectChanges();
    });
  }

  cancelDelete() {
    this.outfitToDelete = null;
  }
}