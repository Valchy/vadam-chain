import { useState } from 'react';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from './components/Select';
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from './components/Table';
import { Button } from './components/Button';
import { Toaster } from './components/Toast';

function App() {
	const [txBtnDisabled, setTxBtnDisabled] = useState(false);

	const handleTransaction = () => {
		setTxBtnDisabled(true);

		setTimeout(() => {
			toast('Transaction successfully sent!');
			setTxBtnDisabled(false);
		}, 2500); // so it looks cooler ;)
	};

	return (
		<div className="flex flex-col gap-6 items-center">
			<div className="flex flex-col items-center">
				<b className="mt-10 text-2xl">VADAM-CHAIN</b>
				<p className="text-slate-500 mb-10 text-sm font-light">When the speed of light is too slow, use vadam-chain.</p>
			</div>
			<div className="flex justify-between items-center w-full max-w-[460px]">
				<div className="flex flex-col">
					<span className="text-center mb-1">Sender</span>
					<Select>
						<SelectTrigger className="w-[180px]">
							<SelectValue placeholder="Select a node" />
						</SelectTrigger>
						<SelectContent>
							<SelectGroup>
								<SelectLabel>Sender</SelectLabel>
								<SelectItem value={0}>Node 1</SelectItem>
								<SelectItem value={1}>Node 2</SelectItem>
								<SelectItem value={2}>Node 3</SelectItem>
							</SelectGroup>
						</SelectContent>
					</Select>
				</div>
				<span className="mt-7">&gt;&gt;&gt;</span>
				<div className="flex flex-col">
					<span className="text-center mb-1">Recepient</span>
					<Select>
						<SelectTrigger className="w-[180px]">
							<SelectValue placeholder="Select a node" />
						</SelectTrigger>
						<SelectContent>
							<SelectGroup>
								<SelectLabel>Recepient</SelectLabel>
								<SelectItem value={0}>Node 1</SelectItem>
								<SelectItem value={1}>Node 2</SelectItem>
								<SelectItem value={2}>Node 3</SelectItem>
							</SelectGroup>
						</SelectContent>
					</Select>
				</div>
			</div>
			<Button onClick={handleTransaction} disabled={txBtnDisabled} className="mt-4 w-[200px]">
				{txBtnDisabled && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
				{txBtnDisabled ? 'Processing...' : 'Send Transaction'}
			</Button>
			<div className="mt-10">
				<div className="flex justify-between items-center mb-5">
					<h2 className="text-center font-light text-md mb-3">Transactions History</h2>
					<Select>
						<SelectTrigger className="w-[180px]">
							<SelectValue placeholder="Select a node" />
						</SelectTrigger>
						<SelectContent>
							<SelectGroup>
								<SelectLabel>Fetch data from</SelectLabel>
								<SelectItem value={0}>Node 1</SelectItem>
								<SelectItem value={1}>Node 2</SelectItem>
								<SelectItem value={2}>Node 3</SelectItem>
							</SelectGroup>
						</SelectContent>
					</Select>
				</div>
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead className="w-[680px]">
								<div className="flex justify-between">
									<span>ID</span>
									<div className="flex justify-between w-[200px]">
										<span>Status</span>
										<span className="text-right">Amount</span>
									</div>
								</div>
							</TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{[1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6].map(i => (
							<TableRow>
								<TableCell className="font-medium">
									<div className="flex justify-between">
										<span>TX-000000{i}</span>
										<div className="flex justify-between w-[200px]">
											<span>Processed</span>
											<span className="text-right">{(Math.random() * (4 - 0.2) + 0.2).toFixed(2)} VAD</span>
										</div>
									</div>
								</TableCell>
							</TableRow>
						))}
					</TableBody>
					<TableCaption>List of all processed transactions.</TableCaption>
				</Table>
			</div>
			<Toaster />
		</div>
	);
}

export default App;
