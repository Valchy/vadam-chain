import { forwardRef } from 'react';

import { cn } from '../lib/utils';
import { ScrollArea } from './Scrollarea';

const Table = forwardRef(({ className, ...props }, ref) => (
	<div className="relative w-full">
		<table ref={ref} className={cn('w-full caption-bottom text-sm', className)} {...props} />
	</div>
));
Table.displayName = 'Table';

const TableHeader = forwardRef(({ className, ...props }, ref) => <thead ref={ref} className={cn('[&_tr]:border-b', className)} {...props} />);
TableHeader.displayName = 'TableHeader';

const TableBody = forwardRef(({ className, ...props }, ref) => (
	<ScrollArea className="h-[280px]">
		<tbody ref={ref} className={cn('[&_tr:last-child]:border-0', className)} {...props} />
	</ScrollArea>
));
TableBody.displayName = 'TableBody';

const TableFooter = forwardRef(({ className, ...props }, ref) => <tfoot ref={ref} className={cn('border-t bg-muted/50 font-medium [&>tr]:last:border-b-0', className)} {...props} />);
TableFooter.displayName = 'TableFooter';

const TableRow = forwardRef(({ className, ...props }, ref) => <tr ref={ref} className={cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', className)} {...props} />);
TableRow.displayName = 'TableRow';

const TableHead = forwardRef(({ className, ...props }, ref) => <th ref={ref} className={cn('h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0', className)} {...props} />);
TableHead.displayName = 'TableHead';

const TableCell = forwardRef(({ className, ...props }, ref) => <td ref={ref} className={cn('p-4 align-middle [&:has([role=checkbox])]:pr-0', className)} {...props} />);
TableCell.displayName = 'TableCell';

const TableCaption = forwardRef(({ className, ...props }, ref) => <caption ref={ref} className={cn('mt-5 text-xs text-muted-foreground', className)} {...props} />);
TableCaption.displayName = 'TableCaption';

export { Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption };
